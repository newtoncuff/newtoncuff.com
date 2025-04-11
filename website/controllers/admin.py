from flask import Blueprint, render_template, request, jsonify, current_app
# Update your SQLAlchemy imports to include type classes directly
from sqlalchemy import MetaData, Table, text, Integer, Float, Boolean, Date, DateTime
from sqlalchemy.sql import expression
from sqlalchemy.ext.declarative import declarative_base
from database.database_schema import query_schema, connect_to_database
from datetime import datetime

# Create the admin blueprint
admin_controller = Blueprint('admin', __name__, url_prefix='/admin')

@admin_controller.route('/')
def index():
    title = "Newton Cuff"
    titleHeader = "Admin Dashboard"
    titleSubHeader = "Manage your database objects"
    return render_template('admin/index.html', title=title, titleHeader=titleHeader, titleSubHeader=titleSubHeader)

@admin_controller.route('/tables')
def list_tables():
    """Get a list of all tables in the database"""
    try:
        # Use the existing database schema module
        engine = connect_to_database()
        db_tables = query_schema(engine)
        
        # Extract table names, excluding SQLAlchemy-internal tables
        table_names = [table.name for table in db_tables 
                      if not table.name.startswith('sqlite_') 
                      and not table.name.startswith('alembic_')]
        
        return jsonify({'tables': table_names})
    except Exception as e:
        current_app.logger.error(f"Error getting tables: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_controller.route('/get-columns')
def get_columns():
    """Get column information for a table"""
    table_name = request.args.get('table')
    if not table_name:
        return jsonify({'error': 'No table specified'}), 400
    
    try:
        # Use the existing database schema module
        engine = connect_to_database()
        db_tables = query_schema(engine)
        
        # Find the requested table
        selected_table = next((table for table in db_tables if table.name == table_name), None)
        if not selected_table:
            return jsonify({'error': f'Table {table_name} not found'}), 404
        
        # Process column information to make it more useful for the frontend
        column_info = []
        for column in selected_table.columns:
            # Determine input type based on column data type
            input_type = 'text'  # Default
            max_length = None
            step = None
            
            # Extract max length from data type if it's a string type
            # For example: "VARCHAR(255)" -> max_length = 255
            if 'VARCHAR(' in column.data_type.upper() or 'CHAR(' in column.data_type.upper():
                try:
                    max_length = int(column.data_type.split('(')[1].split(')')[0])
                except (IndexError, ValueError):
                    pass
            
            # Map data types to HTML input types
            data_type = column.data_type.upper()
            
            if 'INT' in data_type or 'INTEGER' in data_type:
                input_type = 'number'
            elif 'FLOAT' in data_type or 'NUMERIC' in data_type or 'DECIMAL' in data_type:
                input_type = 'number'
                step = '0.01'
            elif 'BOOL' in data_type:
                input_type = 'checkbox'
            elif 'DATE' in data_type and 'TIME' not in data_type:
                input_type = 'date'
            elif 'TIME' in data_type or 'DATETIME' in data_type:
                input_type = 'datetime-local'
            elif 'TEXT' in data_type or (max_length and max_length > 100):
                input_type = 'textarea'
            
            # Get nullable status - assume non-primary keys are nullable unless specified
            # This is a simplification; in production you'd want to check the actual nullable status
            nullable = not column.primary_key
            
            column_info.append({
                'name': column.name,
                'type': column.data_type,
                'nullable': nullable,
                'primary_key': column.primary_key,
                'input_type': input_type,
                'max_length': max_length,
                'step': step,
                'default': None  # Default value info not available from your schema
            })
        
        return jsonify({'columns': column_info})
    except Exception as e:
        current_app.logger.error(f"Error getting columns for {table_name}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_controller.route('/objects', methods=['GET'])
def get_objects():
    """Get all objects from a table"""
    current_app.logger.info("Objects endpoint called")
    
    table_name = request.args.get('table')
    if not table_name:
        current_app.logger.error("No table name provided")
        return jsonify({'error': 'No table specified'}), 400
    
    current_app.logger.info(f"Fetching objects for table: {table_name}")
    
    try:
        # Get table metadata using your schema module
        engine = connect_to_database()
        current_app.logger.info(f"Connected to database successfully")
        
        # Use raw SQL for simple querying - this should work regardless of SQLAlchemy version
        query = f"SELECT * FROM {table_name}"
        current_app.logger.info(f"Executing query: {query}")
        
        # Execute the query using a connection from the engine
        with engine.connect() as connection:
            result = connection.execute(text(query))
            
            # Convert to list of dicts
            objects = []
            for row in result:
                obj = {}
                for column, value in row._mapping.items():
                    # Handle special types like datetime for JSON serialization
                    if isinstance(value, datetime):
                        obj[column] = value.isoformat()
                    else:
                        obj[column] = value
                objects.append(obj)
        
        current_app.logger.info(f"Found {len(objects)} objects")
        return jsonify({'objects': objects})
    except Exception as e:
        current_app.logger.error(f"Error fetching objects: {str(e)}")
        # Return a more detailed error message to help with debugging
        error_details = {
            'error': str(e),
            'type': str(type(e).__name__),
            'table': table_name
        }
        return jsonify(error_details), 500

@admin_controller.route('/create', methods=['POST'])
def create_object():
    """Create a new object in a table"""
    current_app.logger.info(f"Create request received: {request.json}")
    
    table_name = request.json.get('table_name')
    if not table_name:
        current_app.logger.error("No table_name specified in request")
        return jsonify({'error': 'No table specified'}), 400

    try:
        # Get table metadata
        engine = connect_to_database()
        metadata = MetaData(bind=engine)
        table = Table(table_name, metadata, autoload_with=engine)
        current_app.logger.info(f"Table columns: {[c.name for c in table.columns]}")

        # Find the primary key column
        primary_key_column = None
        primary_key_name = 'id'  # Default
        for column in table.columns:
            if column.primary_key:
                primary_key_column = column
                primary_key_name = column.name
                current_app.logger.info(f"Found primary key column: {column.name}")
                break
                
        # Build data dictionary from JSON payload
        data = request.json.get('data', {})
        current_app.logger.info(f"Create data for table '{table_name}': {data}")
        
        if not data:
            current_app.logger.error("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400

        # Validate and process data
        processed_data = {}
        for column in table.columns:
            # Skip the ID/primary key column as it's typically auto-increment
            if column.primary_key:
                current_app.logger.info(f"Skipping primary key column: {column.name}")
                continue

            column_name = column.name
            value = data.get(column_name)
            current_app.logger.info(f"Processing column: {column_name}, value: {value}, type: {type(value) if value is not None else None}")

            # Handle empty values for nullable columns
            if (value is None or value == '') and column.nullable:
                current_app.logger.info(f"Setting NULL for nullable column: {column_name}")
                processed_data[column_name] = None
            elif value is not None:
                # Get column type name for debugging
                column_type = column.type.__class__.__name__
                current_app.logger.info(f"Column {column_name} type: {column_type}")
                
                # Convert based on column type - using directly imported types
                try:
                    if isinstance(column.type, Integer) or 'int' in column_type.lower():
                        processed_data[column_name] = int(value) if value else 0
                        current_app.logger.info(f"Converted {column_name} to integer: {processed_data[column_name]}")
                    elif isinstance(column.type, Float) or any(x in column_type.lower() for x in ['float', 'numeric', 'decimal']):
                        processed_data[column_name] = float(value) if value else 0.0
                        current_app.logger.info(f"Converted {column_name} to float: {processed_data[column_name]}")
                    elif isinstance(column.type, Boolean) or 'bool' in column_type.lower():
                        if isinstance(value, bool):
                            processed_data[column_name] = value
                        else:
                            processed_data[column_name] = value.lower() in ('true', 'yes', '1', 't', 'y') if isinstance(value, str) else bool(value)
                        current_app.logger.info(f"Converted {column_name} to boolean: {processed_data[column_name]}")
                    elif isinstance(column.type, Date) or ('date' in column_type.lower() and 'time' not in column_type.lower()):
                        if value and isinstance(value, str):
                            processed_data[column_name] = datetime.strptime(value, '%Y-%m-%d').date()
                            current_app.logger.info(f"Converted {column_name} to date: {processed_data[column_name]}")
                        else:
                            processed_data[column_name] = None
                    elif isinstance(column.type, DateTime) or 'datetime' in column_type.lower():
                        if value and isinstance(value, str):
                            # Try different datetime formats
                            try:
                                processed_data[column_name] = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
                            except ValueError:
                                try:
                                    processed_data[column_name] = datetime.strptime(value, '%Y-%m-%dT%H:%M')
                                except ValueError:
                                    processed_data[column_name] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            current_app.logger.info(f"Converted {column_name} to datetime: {processed_data[column_name]}")
                        else:
                            processed_data[column_name] = None
                    else:
                        processed_data[column_name] = value
                        current_app.logger.info(f"Using value as is for {column_name}: {value}")
                except Exception as type_error:
                    current_app.logger.error(f"Type conversion error for {column_name}: {str(type_error)}")
                    # Fall back to using value as is
                    processed_data[column_name] = value

        current_app.logger.info(f"Final processed data: {processed_data}")

        current_app.logger.info(f"Final processed data: {processed_data}")

        from sqlalchemy import text
        
        # Build the INSERT statement
        columns = list(processed_data.keys())
        placeholders = [f":{col}" for col in columns]
        
        sql_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        current_app.logger.info(f"SQL Query: {sql_query}")
        current_app.logger.info(f"Parameters: {processed_data}")
        
        new_id = None
        try:
            current_app.logger.info(f"Executing insert statement for {table_name}")
            # Use a transaction context manager that's compatible with older versions
            connection = engine.connect()
            trans = connection.begin()
            try:
                # Execute insert
                connection.execute(text(sql_query), processed_data)
                
                # Get the newly inserted ID using a separate query
                # This works for SQLite and most databases when there's an auto-increment PK
                select_query = f"SELECT MAX({primary_key_name}) as new_id FROM {table_name}"
                id_result = connection.execute(text(select_query)).fetchone()
                if id_result and id_result[0]:
                    new_id = id_result[0]
                    current_app.logger.info(f"Got newly inserted ID from MAX query: {new_id}")
                
                trans.commit()
                current_app.logger.info(f"Insert successful. New ID: {new_id}")
            except Exception as inner_error:
                try:
                    trans.rollback()
                except:
                    current_app.logger.warning("Could not rollback transaction (already closed)")
                current_app.logger.error(f"Error during SQL execution: {str(inner_error)}")
                raise inner_error
            finally:
                connection.close()
        except Exception as sql_error:
            current_app.logger.error(f"SQL execution error: {str(sql_error)}")
            raise sql_error

        return jsonify({
            'success': True,
            'message': f'Successfully created new {table_name} object',
            'id': new_id
        })
    except Exception as e:
        current_app.logger.error(f"Error creating object in {table_name}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_controller.route('/update', methods=['POST'])
def update_object():
    """Update an existing object in a table"""
    current_app.logger.info(f"Update request received: {request.json}")
    
    table_name = request.json.get('table_name')
    if not table_name:
        current_app.logger.error("No table_name specified in request")
        return jsonify({'error': 'No table specified'}), 400

    try:
        # Get the JSON data from the request
        data = request.json.get('data')
        current_app.logger.info(f"Update data for table '{table_name}': {data}")
        
        if not data:
            current_app.logger.error("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400

        if 'id' not in data:
            current_app.logger.error("No ID provided in data")
            return jsonify({'error': 'No ID provided'}), 400

        object_id = data['id']
        current_app.logger.info(f"Updating object ID: {object_id} in table: {table_name}")

        # Get table metadata
        engine = connect_to_database()
        metadata = MetaData(bind=engine)
        table = Table(table_name, metadata, autoload_with=engine)
        current_app.logger.info(f"Table columns: {[c.name for c in table.columns]}")

        # Find the primary key column first
        primary_key_column = None
        for column in table.columns:
            if column.primary_key:
                primary_key_column = column
                current_app.logger.info(f"Found primary key column: {column.name}")
                break
                
        if primary_key_column is None:
            current_app.logger.error(f"No primary key column found for table {table_name}")
            return jsonify({'error': f'No primary key found for table {table_name}'}), 500

        # ADD THIS MISSING SECTION: Process the data to create update_data dictionary
        # Validate and process data
        update_data = {}
        for column in table.columns:
            # Skip the primary key column as it's not updated
            if column.primary_key:
                current_app.logger.info(f"Skipping primary key column: {column.name}")
                continue

            column_name = column.name
            if column_name in data:
                value = data[column_name]
                current_app.logger.info(f"Processing column: {column_name}, value: {value}, type: {type(value) if value is not None else None}")

                # Handle empty values for nullable columns
                if (value is None or value == '') and column.nullable:
                    current_app.logger.info(f"Setting NULL for nullable column: {column_name}")
                    update_data[column_name] = None
                elif value is not None:
                    # Get column type name for debugging
                    column_type = column.type.__class__.__name__
                    current_app.logger.info(f"Column {column_name} type: {column_type}")
                    
                    # Convert based on column type - using directly imported types
                    try:
                        if isinstance(column.type, Integer) or 'int' in column_type.lower():
                            update_data[column_name] = int(value) if value else 0
                            current_app.logger.info(f"Converted {column_name} to integer: {update_data[column_name]}")
                        elif isinstance(column.type, Float) or any(x in column_type.lower() for x in ['float', 'numeric', 'decimal']):
                            update_data[column_name] = float(value) if value else 0.0
                            current_app.logger.info(f"Converted {column_name} to float: {update_data[column_name]}")
                        elif isinstance(column.type, Boolean) or 'bool' in column_type.lower():
                            if isinstance(value, bool):
                                update_data[column_name] = value
                            else:
                                update_data[column_name] = value.lower() in ('true', 'yes', '1', 't', 'y') if isinstance(value, str) else bool(value)
                            current_app.logger.info(f"Converted {column_name} to boolean: {update_data[column_name]}")
                        elif isinstance(column.type, Date) or ('date' in column_type.lower() and 'time' not in column_type.lower()):
                            if value and isinstance(value, str):
                                update_data[column_name] = datetime.strptime(value, '%Y-%m-%d').date()
                                current_app.logger.info(f"Converted {column_name} to date: {update_data[column_name]}")
                            else:
                                update_data[column_name] = None
                        elif isinstance(column.type, DateTime) or 'datetime' in column_type.lower():
                            if value and isinstance(value, str):
                                # Try different datetime formats
                                try:
                                    update_data[column_name] = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
                                except ValueError:
                                    try:
                                        update_data[column_name] = datetime.strptime(value, '%Y-%m-%dT%H:%M')
                                    except ValueError:
                                        update_data[column_name] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                                current_app.logger.info(f"Converted {column_name} to datetime: {update_data[column_name]}")
                            else:
                                update_data[column_name] = None
                        else:
                            update_data[column_name] = value
                            current_app.logger.info(f"Using value as is for {column_name}: {value}")
                    except Exception as type_error:
                        current_app.logger.error(f"Type conversion error for {column_name}: {str(type_error)}")
                        # Fall back to using value as is
                        update_data[column_name] = value

        current_app.logger.info(f"Final update data: {update_data}")

        # Check if we have any data to update
        if not update_data:
            current_app.logger.warning(f"No valid data to update for object ID {object_id} in table {table_name}")
            return jsonify({
                'success': True,
                'message': f'No changes to update for {table_name} object with ID {object_id}'
            })

        primary_key_name = primary_key_column.name
        current_app.logger.info(f"Using primary key column: {primary_key_name}")

        from sqlalchemy import text
        
        # Build SET clause of the SQL UPDATE statement
        set_clauses = []
        params = {"primary_id": object_id}
        
        for col_name, val in update_data.items():
            set_clauses.append(f"{col_name} = :{col_name}")
            params[col_name] = val
            
        set_clause = ", ".join(set_clauses)
        sql_query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key_name} = :primary_id"
        
        current_app.logger.info(f"SQL Query: {sql_query}")
        current_app.logger.info(f"Parameters: {params}")
        
        try:
            current_app.logger.info(f"Executing update statement for {table_name}.{primary_key_name} = {object_id}")
            # Use a transaction context manager that's compatible with older versions
            connection = engine.connect()
            trans = connection.begin()
            try:
                result = connection.execute(text(sql_query), params)
                trans.commit()
                current_app.logger.info(f"Update result: {result.rowcount} rows affected")
            except:
                trans.rollback()
                raise
            finally:
                connection.close()
                
        except Exception as sql_error:
            current_app.logger.error(f"SQL execution error: {str(sql_error)}")
            raise sql_error

        return jsonify({
            'success': True,
            'message': f'Successfully updated {table_name} object with ID {object_id}'
        })
    except Exception as e:
        current_app.logger.error(f"Error updating object in {table_name}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_controller.route('/delete', methods=['DELETE'])
def delete_object():
    """Delete an object from a table"""
    current_app.logger.info("Delete request received")
    
    table_name = request.args.get('table')
    object_id = request.args.get('id')
    
    current_app.logger.info(f"Delete request for table: {table_name}, object ID: {object_id}")
    
    if not table_name:
        current_app.logger.error("No table specified in request")
        return jsonify({'error': 'No table specified'}), 400
    
    if not object_id:
        current_app.logger.error("No ID specified in request")
        return jsonify({'error': 'No ID specified'}), 400
    
    try:
        # Get table metadata
        engine = connect_to_database()
        metadata = MetaData(bind=engine)
        table = Table(table_name, metadata, autoload_with=engine)
        current_app.logger.info(f"Table columns: {[c.name for c in table.columns]}")
        
        # Find the primary key column
        primary_key_column = None
        for column in table.columns:
            if column.primary_key:
                primary_key_column = column
                current_app.logger.info(f"Found primary key column: {column.name}")
                break
                
        if primary_key_column is None:
            current_app.logger.error(f"No primary key column found for table {table_name}")
            return jsonify({'error': f'No primary key found for table {table_name}'}), 500
        
        primary_key_name = primary_key_column.name
        current_app.logger.info(f"Using primary key column: {primary_key_name}")
        
        # Use raw SQL with text()
        from sqlalchemy import text
        
        # Construct the SQL statement
        sql = f"DELETE FROM {table_name} WHERE {primary_key_name} = :id"
        params = {'id': object_id}
        
        current_app.logger.info(f"SQL Query: {sql}")
        current_app.logger.info(f"Parameters: {params}")
        
        try:
            current_app.logger.info(f"Executing delete statement for {table_name}.{primary_key_name} = {object_id}")
            # Use a transaction context manager that's compatible with older versions
            connection = engine.connect()
            trans = connection.begin()
            try:
                result = connection.execute(text(sql), params)
                trans.commit()
                current_app.logger.info(f"Delete result: {result.rowcount} rows affected")
                
                if result.rowcount == 0:
                    current_app.logger.warning(f"No object found with ID {object_id} in table {table_name}")
                    return jsonify({'error': f'No object found with ID {object_id} in table {table_name}'}), 404
            except Exception as inner_error:
                trans.rollback()
                current_app.logger.error(f"Error during SQL execution: {str(inner_error)}")
                raise inner_error
            finally:
                connection.close()
                
        except Exception as sql_error:
            current_app.logger.error(f"SQL execution error: {str(sql_error)}")
            raise sql_error
        
        return jsonify({
            'success': True, 
            'message': f'Successfully deleted {table_name} object with ID {object_id}'
        })
    except Exception as e:
        current_app.logger.error(f"Error deleting object from {table_name}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500