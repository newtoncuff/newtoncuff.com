document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const objectTypeSelect = document.getElementById('object-type');
    const contentContainer = document.getElementById('content-container');
    const panelTitle = document.getElementById('panel-title');
    const createActionsDiv = document.getElementById('create-actions');
    const submitBtn = document.getElementById('submit-btn');
    const createNewBtn = document.getElementById('create-new-btn');
    const viewAllBtn = document.getElementById('view-all-btn');
    const viewModeControls = document.getElementById('view-mode-controls');
    const refreshDataBtn = document.getElementById('refresh-data-btn');
    const searchInput = document.getElementById('search-input');
    const paginationControls = document.getElementById('pagination-controls');
    
    // State variables
    let currentMode = 'none'; // 'create' or 'view'
    let currentPage = 1;
    let itemsPerPage = 10;
    let totalItems = 0;
    let objectData = [];
    let filteredData = [];
    
    // Fetch available tables from the backend
    fetch('/admin/tables')
      .then(response => response.json())
      .then(data => {
        // Clear any existing options except the placeholder
        while (objectTypeSelect.options.length > 1) {
          objectTypeSelect.remove(1);
        }
        
        // Add options from the fetched tables
        if (data.tables && Array.isArray(data.tables)) {
          data.tables.forEach(table => {
            const option = document.createElement('option');
            option.value = table;
            option.textContent = table.charAt(0).toUpperCase() + table.slice(1);
            objectTypeSelect.appendChild(option);
          });
        } else {
          // Add some placeholder options if data couldn't be fetched
          const placeholderOptions = ['Delusions', 'Thoughts', 'Interests', 'Passions'];
          placeholderOptions.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option.toLowerCase();
            opt.textContent = option;
            objectTypeSelect.appendChild(opt);
          });
        }
      })
      .catch(error => {
        console.error('Error fetching tables:', error);
        
        // Add placeholder options in case of error
        const placeholderOptions = ['Delusions', 'Thoughts', 'Interests', 'Passions'];
        placeholderOptions.forEach(option => {
          const opt = document.createElement('option');
          opt.value = option.toLowerCase();
          opt.textContent = option;
          objectTypeSelect.appendChild(opt);
        });
      });
    
    // Handle object type selection change - now only updates the button states
    objectTypeSelect.addEventListener('change', function() {
      const selectedValue = this.value;
      
      // Enable/disable action buttons based on selection
      if (selectedValue) {
        createNewBtn.classList.remove('disabled');
        viewAllBtn.classList.remove('disabled');
      } else {
        createNewBtn.classList.add('disabled');
        viewAllBtn.classList.add('disabled');
      }
      
      // Reset the content area to show selection message
      if (currentMode !== 'none') {
        currentMode = 'none';
        resetContentArea();
      }
    });
    
    // Reset content area to initial state
    function resetContentArea() {
      contentContainer.innerHTML = `
        <div class="form-message">
          Please select an action using the buttons above
        </div>
      `;
      panelTitle.textContent = "Database Object Details";
      createActionsDiv.style.display = 'none';
      viewModeControls.style.display = 'none';
      paginationControls.style.display = 'none';
    }
    
    // Switch to create mode
    function switchToCreateMode(objectType) {
      currentMode = 'create';
      panelTitle.textContent = `Create New ${objectType.charAt(0).toUpperCase() + objectType.slice(1)}`;
      
      // Show loading state
      contentContainer.innerHTML = `
        <div style="text-align: center; padding: 40px;">
          <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; 
                  border-radius: 50%; border-top: 4px solid #d2b356; animation: spin 1s linear infinite;"></div>
          <p style="margin-top: 20px; color: #666;">Loading form fields...</p>
        </div>
      `;
      
      // Hide view controls, show create controls
      viewModeControls.style.display = 'none';
      paginationControls.style.display = 'none';
      createActionsDiv.style.display = 'block';
      
      // Fetch the columns for the selected table
      fetch(`/admin/get-columns?table=${objectType}`)
        .then(response => response.json())
        .then(data => {
          if (data.columns && data.columns.length > 0) {
            // Create form with fields
            const form = document.createElement('form');
            form.id = 'create-form';
            
            // Add hidden field for table name
            const tableInput = document.createElement('input');
            tableInput.type = 'hidden';
            tableInput.name = 'table_name';
            tableInput.value = objectType;
            form.appendChild(tableInput);
            
            // Generate form fields for each column
            data.columns.forEach(column => {
              // Skip ID field as it's not editable
              if (column.primary_key) return;
              
              const formGroup = document.createElement('div');
              formGroup.className = 'form-group';
              
              const label = document.createElement('label');
              label.htmlFor = column.name;
              label.textContent = column.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
              if (!column.nullable) {
                label.className = 'required-field';
              }
              formGroup.appendChild(label);
              
              let input;
              
              // Create appropriate input type based on column type
              if (column.input_type === 'textarea') {
                input = document.createElement('textarea');
                input.rows = 4;
              } else if (column.input_type === 'checkbox') {
                input = document.createElement('input');
                input.type = 'checkbox';
                if (column.default) {
                  input.checked = true;
                }
              } else {
                input = document.createElement('input');
                input.type = column.input_type;
                
                if (column.input_type === 'number' && column.step) {
                  input.step = column.step;
                }
              }
              
              // Set common attributes
              input.id = column.name;
              input.name = column.name;
              if (column.default !== null && column.input_type !== 'checkbox') {
                input.value = column.default;
              }
              if (!column.nullable) {
                input.required = true;
              }
              if (column.max_length) {
                input.maxLength = column.max_length;
                
                // Add note about max length
                const helpText = document.createElement('small');
                helpText.textContent = `Maximum length: ${column.max_length}`;
                helpText.style.display = 'block';
                helpText.style.marginTop = '4px';
                helpText.style.color = '#666';
                formGroup.appendChild(helpText);
              }
              
              formGroup.insertBefore(input, formGroup.querySelector('small'));
              form.appendChild(formGroup);
            });
            
            // Clear the container and add the form
            contentContainer.innerHTML = '';
            contentContainer.appendChild(form);
          } else {
            contentContainer.innerHTML = `
              <div class="form-message">
                No columns found for this object type
              </div>
            `;
            createActionsDiv.style.display = 'none';
          }
        })
        .catch(error => {
          console.error('Error fetching columns:', error);
          contentContainer.innerHTML = `
            <div class="form-message" style="color: #e74c3c;">
              Error loading form fields. Please try again.
            </div>
          `;
          createActionsDiv.style.display = 'none';
        });
    }
    
    // Switch to view mode and load objects
    function switchToViewMode(objectType) {
      currentMode = 'view';
      panelTitle.textContent = `${objectType.charAt(0).toUpperCase() + objectType.slice(1)} List`;
      
      // Hide create controls, show view controls
      createActionsDiv.style.display = 'none';
      viewModeControls.style.display = 'flex';
      
      // Load object data
      loadObjectList(objectType);
    }
    
    // Load objects for the given type
    function loadObjectList(objectType) {
      // Show loading state
      contentContainer.innerHTML = `
        <div style="text-align: center; padding: 40px;">
          <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; 
                  border-radius: 50%; border-top: 4px solid #d2b356; animation: spin 1s linear infinite;"></div>
          <p style="margin-top: 20px; color: #666;">Loading ${objectType}...</p>
        </div>
      `;
      
      // Fetch objects of the selected type
      fetch(`/admin/objects?table=${objectType}`)
        .then(response => response.json())
        .then(data => {
          if (data.objects && data.objects.length > 0) {
            objectData = data.objects;
            filteredData = [...objectData];
            totalItems = filteredData.length;
            
            // Set up pagination
            updatePagination();
            paginationControls.style.display = 'flex';
            
            // Render the first page of objects
            renderObjectList();
          } else {
            contentContainer.innerHTML = `
              <div class="no-data">
                <p>No ${objectType} found.</p>
                <button id="create-first-btn" class="submit-btn" style="margin-top: 15px;">Create First ${objectType}</button>
              </div>
            `;
            paginationControls.style.display = 'none';
            
            // Add event listener to the "Create First" button
            document.getElementById('create-first-btn').addEventListener('click', function() {
              switchToCreateMode(objectType);
            });
          }
        })
        .catch(error => {
          console.error('Error fetching objects:', error);
          contentContainer.innerHTML = `
            <div class="form-message" style="color: #e74c3c;">
              Error loading objects. Please try again.
              <br><br>
              <pre>${error.toString()}</pre>
            </div>
          `;
          paginationControls.style.display = 'none';
        });
    }
    
    // Render object list with pagination
    function renderObjectList() {
      // Get column info for the selected object type
      const objectType = objectTypeSelect.value;
      
      fetch(`/admin/get-columns?table=${objectType}`)
        .then(response => response.json())
        .then(columnData => {
          if (!columnData.columns || columnData.columns.length === 0) {
            throw new Error('No column information available');
          }
          
          // Calculate pagination slices
          const startIndex = (currentPage - 1) * itemsPerPage;
          const endIndex = startIndex + itemsPerPage;
          const paginatedData = filteredData.slice(startIndex, endIndex);
          
          if (paginatedData.length === 0) {
            contentContainer.innerHTML = `
              <div class="no-data">
                <p>No ${objectType} found matching your search.</p>
              </div>
            `;
            return;
          }
          
          // Create list container
          const listContainer = document.createElement('div');
          listContainer.className = 'object-list';
          
          // Create accordions for each object
          paginatedData.forEach((object, index) => {
            // Create accordion
            const accordion = document.createElement('div');
            accordion.className = 'object-accordion';
            accordion.dataset.objectId = object.id;
            
            // Create accordion header
            const header = document.createElement('div');
            header.className = 'accordion-header';
            
            // Determine what to show in the header
            let headerTitle = `${objectType} #${object.id}`;
            if (object.topic) headerTitle = object.topic;
            else if (object.title) headerTitle = object.title;
            else if (object.name) headerTitle = object.name;
            
            header.innerHTML = `
              <span>${headerTitle}</span>
              <span class="accordion-icon">▼</span>
            `;
            
            // Create accordion content
            const content = document.createElement('div');
            content.className = 'accordion-content';
            
            // Create form for editing
            const form = document.createElement('form');
            form.className = 'accordion-form';
            form.dataset.objectId = object.id;
            
            // Add hidden field for ID
            const idInput = document.createElement('input');
            idInput.type = 'hidden';
            idInput.name = 'id';
            idInput.value = object.id;
            form.appendChild(idInput);
            
            // Generate form fields for each column
            columnData.columns.forEach(column => {
              // Skip ID field as it's not editable
              if (column.name.toLowerCase() === 'id' || column.primary_key) return;
              
              const formGroup = document.createElement('div');
              formGroup.className = 'accordion-form-group';
              
              const label = document.createElement('label');
              label.htmlFor = `${column.name}_${object.id}`;
              label.textContent = column.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
              if (!column.nullable) {
                label.className = 'required-field';
              }
              formGroup.appendChild(label);
              
              let input;
              const value = object[column.name];
              
              // Create appropriate input type based on column type
              if (column.input_type === 'textarea') {
                input = document.createElement('textarea');
                input.rows = 3;
                input.value = value || '';
              } else if (column.input_type === 'checkbox') {
                input = document.createElement('input');
                input.type = 'checkbox';
                input.checked = Boolean(value);
              } else {
                input = document.createElement('input');
                input.type = column.input_type;
                input.value = value !== null && value !== undefined ? value : '';
                
                if (column.input_type === 'number' && column.step) {
                  input.step = column.step;
                }
              }
              
              // Set common attributes
              input.id = `${column.name}_${object.id}`;
              input.name = column.name;
              if (!column.nullable) {
                input.required = true;
              }
              if (column.max_length) {
                input.maxLength = column.max_length;
              }
              
              formGroup.appendChild(input);
              form.appendChild(formGroup);
            });
            
            // Add action buttons
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'object-actions';
            actionsDiv.innerHTML = `
              <button type="button" class="update-btn" data-id="${object.id}">Update</button>
              <button type="button" class="delete-btn" data-id="${object.id}">Delete</button>
            `;
            
            // Append form and actions to content
            content.appendChild(form);
            content.appendChild(actionsDiv);
            
            // Append header and content to accordion
            accordion.appendChild(header);
            accordion.appendChild(content);
            
            // Add accordion to list container
            listContainer.appendChild(accordion);
            
            // Add event listeners for accordion toggle
            header.addEventListener('click', function() {
              this.classList.toggle('active');
              const content = this.nextElementSibling;
              if (content.style.display === 'block') {
                content.style.display = 'none';
              } else {
                content.style.display = 'block';
              }
            });
            
            // Add event listeners for update and delete buttons
            const updateBtn = actionsDiv.querySelector('.update-btn');
            updateBtn.addEventListener('click', function() {
              const objectId = this.dataset.id;
              const form = document.querySelector(`.accordion-form[data-object-id="${objectId}"]`);
              
              // Validate form
              const isValid = Array.from(form.querySelectorAll('[required]')).every(input => input.value.trim() !== '');
              if (!isValid) {
                alert('Please fill in all required fields.');
                return;
              }
              
              // Collect form data
              const formData = {};
              formData.id = objectId;
              
              // Add all form fields
              form.querySelectorAll('input:not([type="checkbox"]), textarea').forEach(input => {
                formData[input.name] = input.value;
              });
              
              // Handle checkboxes separately
              form.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                formData[checkbox.name] = checkbox.checked;
              });
              
              // Update button state
              const originalText = this.textContent;
              this.innerHTML = '<span class="loading-spinner"></span> Updating...';
              this.disabled = true;
              
              // Send update request
              const requestData = {
                table_name: objectType,
                data: formData
              };

              // Add debugging console logs
              console.log('Update request payload:', requestData);
              console.log('Form data collected:', formData);
              console.log('Object type:', objectType);
              console.log('Object ID:', objectId);
              
              fetch(`/admin/update`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
              })
              .then(response => {
                if (!response.ok) {
                  throw new Error('Update failed');
                }
                return response.json();
              })
              .then(data => {
                alert('Object updated successfully!');
                this.innerHTML = originalText;
                this.disabled = false;
              })
              .catch(error => {
                alert(`Update failed: ${error.message}`);
                this.innerHTML = originalText;
                this.disabled = false;
              });
            });
            
            const deleteBtn = actionsDiv.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', function() {
              const objectId = this.dataset.id;
              if (confirm(`Are you sure you want to delete this ${objectType}?`)) {
                // Send delete request
                fetch(`/admin/delete?table=${objectType}&id=${objectId}`, {
                  method: 'DELETE'
                })
                .then(response => {
                  if (!response.ok) {
                    throw new Error('Delete failed');
                  }
                  return response.json();
                })
                .then(data => {
                  alert('Object deleted successfully!');
                  // Remove the accordion from the UI
                  const accordion = document.querySelector(`.object-accordion[data-object-id="${objectId}"]`);
                  accordion.remove();
                  
                  // Update object data and pagination
                  objectData = objectData.filter(obj => obj.id != objectId);
                  filteredData = filteredData.filter(obj => obj.id != objectId);
                  totalItems = filteredData.length;
                  updatePagination();
                  
                  // If no more objects on this page and not the first page, go to previous page
                  const startIndex = (currentPage - 1) * itemsPerPage;
                  if (startIndex >= filteredData.length && currentPage > 1) {
                    currentPage--;
                    renderObjectList();
                  } else if (filteredData.length === 0) {
                    // If no more objects at all
                    contentContainer.innerHTML = `
                      <div class="no-data">
                        <p>No ${objectType} found.</p>
                        <button id="create-first-btn" class="submit-btn" style="margin-top: 15px;">Create First ${objectType}</button>
                      </div>
                    `;
                    paginationControls.style.display = 'none';
                    
                    // Add event listener to the "Create First" button
                    document.getElementById('create-first-btn').addEventListener('click', function() {
                      switchToCreateMode(objectType);
                    });
                  }
                })
                .catch(error => {
                  alert(`Delete failed: ${error.message}`);
                });
              }
            });
          });
          
          // Clear the container and add the list
          contentContainer.innerHTML = '';
          contentContainer.appendChild(listContainer);
        })
        .catch(error => {
          console.error('Error rendering object list:', error);
          contentContainer.innerHTML = `
            <div class="form-message" style="color: #e74c3c;">
              Error rendering objects. Please try again.
              <br><br>
              <pre>${error.toString()}</pre>
            </div>
          `;
        });
    }
    
    // Update pagination controls
    function updatePagination() {
      const totalPages = Math.ceil(totalItems / itemsPerPage);
      document.getElementById('current-page').textContent = currentPage;
      document.getElementById('total-pages').textContent = totalPages;
      
      // Update button states
      const buttons = paginationControls.querySelectorAll('.pagination-btn');
      buttons.forEach(button => {
        button.disabled = false;
        
        if ((button.dataset.page === 'first' || button.dataset.page === 'prev') && currentPage === 1) {
          button.disabled = true;
        }
        
        if ((button.dataset.page === 'last' || button.dataset.page === 'next') && currentPage === totalPages) {
          button.disabled = true;
        }
      });
    }
    
    // Handle pagination button clicks
    paginationControls.addEventListener('click', function(e) {
      if (e.target.classList.contains('pagination-btn')) {
        const action = e.target.dataset.page;
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        
        if (action === 'first') {
          currentPage = 1;
        } else if (action === 'prev') {
          currentPage = Math.max(1, currentPage - 1);
        } else if (action === 'next') {
          currentPage = Math.min(totalPages, currentPage + 1);
        } else if (action === 'last') {
          currentPage = totalPages;
        }
        
        renderObjectList();
        updatePagination();
      }
    });
    
    // Handle search input
    searchInput.addEventListener('input', debounce(function() {
      const searchTerm = this.value.toLowerCase();
      
      if (searchTerm === '') {
        filteredData = [...objectData];
      } else {
        filteredData = objectData.filter(object => {
          return Object.values(object).some(value => {
            return value !== null && 
                  String(value).toLowerCase().includes(searchTerm);
          });
        });
      }
      
      totalItems = filteredData.length;
      currentPage = 1;
      updatePagination();
      renderObjectList();
    }, 300));
    
    // Debounce function for search input
    function debounce(func, wait) {
      let timeout;
      return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
      };
    }
    
    // Handle refresh button
    refreshDataBtn.addEventListener('click', function() {
      const objectType = objectTypeSelect.value;
      loadObjectList(objectType);
    });
    
    // Handle create new button click
    createNewBtn.addEventListener('click', function(e) {
      e.preventDefault();
      
      // If an object type is selected, switch to create mode
      const selectedValue = objectTypeSelect.value;
      if (selectedValue) {
        switchToCreateMode(selectedValue);
      } else {
        // Show a message to select an object type first
        alert('Please select an object type from the dropdown first');
      }
    });
    
    // Handle view all button click
    viewAllBtn.addEventListener('click', function(e) {
      e.preventDefault();
      
      // If an object type is selected, switch to view mode
      const selectedValue = objectTypeSelect.value;
      if (selectedValue) {
        switchToViewMode(selectedValue);
      } else {
        // Show a message to select an object type first
        alert('Please select an object type from the dropdown first');
      }
    });
    
    // Handle submit button click for creating new objects
    submitBtn.addEventListener('click', function() {
      const form = document.getElementById('create-form');
      
      if (form) {
        // Basic form validation
        const isValid = form.checkValidity();
        if (!isValid) {
          form.reportValidity();
          return;
        }
        
        // Show loading state on button
        const originalText = this.innerHTML;
        this.innerHTML = '<span class="loading-spinner"></span> Saving...';
        this.disabled = true;
        
        // Collect form data
        const objectType = objectTypeSelect.value;
        
        // Create data object for the API
        const formData = {};
        
        // Add all form fields except hidden table_name
        form.querySelectorAll('input:not([type="hidden"]):not([type="checkbox"]), textarea').forEach(input => {
          formData[input.name] = input.value;
        });
        
        // Handle checkboxes separately
        form.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
          formData[checkbox.name] = checkbox.checked;
        });
        
        // Create the request payload
        const requestData = {
          table_name: objectType,
          data: formData
        };
        
        // Submit the form
        fetch('/admin/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          // Show success message
          contentContainer.innerHTML = `
            <div class="form-message" style="color: #2ecc71;">
              <p><strong>Success!</strong> Object created successfully.</p>
              <p>You can create another ${objectType} or view all objects.</p>
            </div>
          `;
          
          // Reset button
          this.innerHTML = originalText;
          this.disabled = false;
        })
        .catch(error => {
          console.error('Error:', error);
          
          // Show error message
          contentContainer.innerHTML = `
            <div class="form-message" style="color: #e74c3c;">
              <p><strong>Error!</strong> Something went wrong while saving.</p>
              <p>${error.message}</p>
              <p>Please try again.</p>
            </div>
          `;
          
          // Reset button
          this.innerHTML = originalText;
          this.disabled = false;
        });
      }
    });
    
    // Add disabled class to buttons initially until an object type is selected
    createNewBtn.classList.add('disabled');
    viewAllBtn.classList.add('disabled');
    
    // Initialize with empty message
    resetContentArea();
  });