-- Create the database
CREATE DATABASE IF NOT EXISTS newtoncuff_com
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE newtoncuff_com;

-- Drop tables if they exist (for clean recreation)
DROP TABLE IF EXISTS Tales;
DROP TABLE IF EXISTS Thoughts;
DROP TABLE IF EXISTS Passions;
DROP TABLE IF EXISTS Delusions;
DROP TABLE IF EXISTS Interests;
DROP TABLE IF EXISTS Users;

-- Create Users table
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    is_admin BIT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Passions table
CREATE TABLE Passions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(100) NOT NULL,
    topicDesc TEXT,
    subtopic VARCHAR(100),
    subTopicDesc TEXT,
    tag VARCHAR(255),
    hasTales BIT(1) NOT NULL DEFAULT 0 COMMENT 'Indicates whether this passion has associated tales',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Delusions table
CREATE TABLE Delusions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(100) NOT NULL,
    topicDesc TEXT,
    subtopic VARCHAR(100),
    subTopicDesc TEXT,
    tag VARCHAR(255),
    hasTales BIT(1) NOT NULL DEFAULT 0 COMMENT 'Indicates whether this delusion has associated tales',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Thoughts table
CREATE TABLE Thoughts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(100) NOT NULL,
    topicDesc TEXT,
    subtopic VARCHAR(100),
    subTopicDesc TEXT,
    tag VARCHAR(255),
    hasTales BIT(1) NOT NULL DEFAULT 0 COMMENT 'Indicates whether this thought has associated tales',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Interests table
CREATE TABLE Interests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(100) NOT NULL,
    topicDesc TEXT,
    subtopic VARCHAR(100),
    subTopicDesc TEXT,
    tag VARCHAR(255),
    hasTales BIT(1) NOT NULL DEFAULT 0 COMMENT 'Indicates whether this interest has associated tales',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Tales table
CREATE TABLE Tales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mindObjectType VARCHAR(50) NOT NULL COMMENT 'Type of mind object (Thoughts, Passions, Skills, Projects)',
    mindObjectTypeId INT NOT NULL COMMENT 'ID of the associated mind object',
    topicTitle VARCHAR(255),
    date DATETIME,
    location VARCHAR(255),
    talltale TEXT NOT NULL,
    userDefined1 VARCHAR(255),
    userDefined2 VARCHAR(255),
    userDefined3 VARCHAR(255),
    userDefined4 VARCHAR(255),
    userDefined5 VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mind_object (mindObjectType, mindObjectTypeId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create a trigger to update the hasTales flag when tales are added
DELIMITER $$

CREATE TRIGGER after_tale_insert
AFTER INSERT ON Tales
FOR EACH ROW
BEGIN
    IF NEW.mindObjectType = 'passions' THEN
        UPDATE Passions SET hasTales = 1 WHERE id = NEW.mindObjectTypeId;
    ELSEIF NEW.mindObjectType = 'thoughts' THEN
        UPDATE Thoughts SET hasTales = 1 WHERE id = NEW.mindObjectTypeId;
    ELSEIF NEW.mindObjectType = 'interests' THEN
        UPDATE Interests SET hasTales = 1 WHERE id = NEW.mindObjectTypeId;
    ELSEIF NEW.mindObjectType = 'delusions' THEN
        UPDATE Delusions SET hasTales = 1 WHERE id = NEW.mindObjectTypeId;
    END IF;
END$$

CREATE TRIGGER after_tale_delete
AFTER DELETE ON Tales
FOR EACH ROW
BEGIN
    IF OLD.mindObjectType = 'passions' THEN
        IF (SELECT COUNT(*) FROM Tales WHERE mindObjectType = 'passions' AND mindObjectTypeId = OLD.mindObjectTypeId) = 0 THEN
            UPDATE Passions SET hasTales = 0 WHERE id = OLD.mindObjectTypeId;
        END IF;
    ELSEIF OLD.mindObjectType = 'thoughts' THEN
        IF (SELECT COUNT(*) FROM Tales WHERE mindObjectType = 'thoughts' AND mindObjectTypeId = OLD.mindObjectTypeId) = 0 THEN
            UPDATE Thoughts SET hasTales = 0 WHERE id = OLD.mindObjectTypeId;
        END IF;
    ELSEIF OLD.mindObjectType = 'interests' THEN
        IF (SELECT COUNT(*) FROM Tales WHERE mindObjectType = 'interests' AND mindObjectTypeId = OLD.mindObjectTypeId) = 0 THEN
            UPDATE Interests SET hasTales = 0 WHERE id = OLD.mindObjectTypeId;
        END IF;
    ELSEIF OLD.mindObjectType = 'delusions' THEN
        IF (SELECT COUNT(*) FROM Tales WHERE mindObjectType = 'delusions' AND mindObjectTypeId = OLD.mindObjectTypeId) = 0 THEN
            UPDATE Delusions SET hasTales = 0 WHERE id = OLD.mindObjectTypeId;
        END IF;
    END IF;
END$$

DELIMITER ;

-- Create a view for consolidated mind objects with tale counts
CREATE OR REPLACE VIEW mind_objects_with_tales AS
SELECT 
    'passions' AS object_type,
    id,
    topic,
    topicDesc,
    subtopic,
    subTopicDesc,
    tag,
    hasTales,
    (SELECT COUNT(*) FROM Tales WHERE mindObjectType = 'passions' AND mindObjectTypeId = Passions.id) AS tale_count
FROM Passions

UNION ALL

SELECT 
    'thoughts' AS object_type,
    id,
    topic,
    topicDesc,
    subtopic,
    subTopicDesc,
    tag,
    hasTales,
    (SELECT COUNT(*) FROM Tales WHERE mindObjectType = 'thoughts' AND mindObjectTypeId = Thoughts.id) AS tale_count
FROM Thoughts

UNION ALL

SELECT 
    'interests' AS object_type,
    id,
    topic,
    topicDesc,
    subtopic,
    subTopicDesc,
    tag,
    hasTales,
    (SELECT COUNT(*) FROM Tales WHERE mindObjectType = 'interests' AND mindObjectTypeId = Interests.id) AS tale_count
FROM Interests

UNION ALL

SELECT 
    'delusions' AS object_type,
    id,
    topic,
    topicDesc,
    subtopic,
    subTopicDesc,
    tag,
    hasTales,
    (SELECT COUNT(*) FROM Tales WHERE mindObjectType = 'delusions' AND mindObjectTypeId = Delusions.id) AS tale_count
FROM Delusions;

-- Create stored procedure to get tales for any mind object
DELIMITER $$

CREATE PROCEDURE get_tales_for_mind_object(
    IN p_object_type VARCHAR(50),
    IN p_object_id INT
)
BEGIN
    SELECT *
    FROM Tales
    WHERE mindObjectType = LOWER(p_object_type)
    AND mindObjectTypeId = p_object_id
    ORDER BY date DESC;
END$$

-- Create stored procedure to search across all mind objects
CREATE PROCEDURE search_mind_objects(
    IN p_search_term VARCHAR(255)
)
BEGIN
    SELECT 
        'passions' AS object_type,
        id,
        topic,
        topicDesc,
        subtopic,
        subTopicDesc,
        tag,
        hasTales
    FROM Passions
    WHERE 
        topic LIKE CONCAT('%', p_search_term, '%') OR
        topicDesc LIKE CONCAT('%', p_search_term, '%') OR
        subtopic LIKE CONCAT('%', p_search_term, '%') OR
        subTopicDesc LIKE CONCAT('%', p_search_term, '%') OR
        tag LIKE CONCAT('%', p_search_term, '%')
    
    UNION ALL
    
    SELECT 
        'thoughts' AS object_type,
        id,
        topic,
        topicDesc,
        subtopic,
        subTopicDesc,
        tag,
        hasTales
    FROM Thoughts
    WHERE 
        topic LIKE CONCAT('%', p_search_term, '%') OR
        topicDesc LIKE CONCAT('%', p_search_term, '%') OR
        subtopic LIKE CONCAT('%', p_search_term, '%') OR
        subTopicDesc LIKE CONCAT('%', p_search_term, '%') OR
        tag LIKE CONCAT('%', p_search_term, '%')
    
    UNION ALL
    
    SELECT 
        'interests' AS object_type,
        id,
        topic,
        topicDesc,
        subtopic,
        subTopicDesc,
        tag,
        hasTales
    FROM Interests
    WHERE 
        topic LIKE CONCAT('%', p_search_term, '%') OR
        topicDesc LIKE CONCAT('%', p_search_term, '%') OR
        subtopic LIKE CONCAT('%', p_search_term, '%') OR
        subTopicDesc LIKE CONCAT('%', p_search_term, '%') OR
        tag LIKE CONCAT('%', p_search_term, '%')

    UNION ALL

    SELECT 
        'delusions' AS object_type,
        id,
        topic,
        topicDesc,
        subtopic,
        subTopicDesc,
        tag,
        hasTales
    FROM Delusions
    WHERE 
        topic LIKE CONCAT('%', p_search_term, '%') OR
        topicDesc LIKE CONCAT('%', p_search_term, '%') OR
        subtopic LIKE CONCAT('%', p_search_term, '%') OR
        subTopicDesc LIKE CONCAT('%', p_search_term, '%') OR
        tag LIKE CONCAT('%', p_search_term, '%'); 
END$$

DELIMITER ;

-- Insert initial admin user (password: admin123)
INSERT INTO Users (username, password, email, first_name, last_name, is_admin)
VALUES ('admin', '$2b$12$tJIxYllXrS.XpXmxpnS0leJgpeiGJydG5JZxJJY.4QR1gayCWNK5m', 'admin@newtoncuff.com', 'Admin', 'User', 1);