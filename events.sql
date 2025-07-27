--ADDING AN EVENT 
CREATE OR REPLACE FUNCTION create_event(
    event_name VARCHAR,
    event_date DATE,
    event_location VARCHAR,
    event_description VARCHAR
) RETURNS VOID AS $$
BEGIN
    INSERT INTO events (event_name, event_date, event_location, event_description)
    VALUES (event_name, event_date, event_location, event_description);
END;
$$ LANGUAGE plpgsql;



--adding event budget

CREATE OR REPLACE PROCEDURE add_event_budget(
    IN p_event_id INT,
    IN p_amount DECIMAL,
    IN p_description TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    
    IF EXISTS (SELECT 1 FROM event WHERE event_id = p_event_id) THEN
        
        INSERT INTO budget (event_id, amount, description)
        VALUES (p_event_id, p_amount, p_description);
    ELSE
        
        RAISE EXCEPTION 'Event with ID % does not exist.', p_event_id;
    END IF;
END;
$$;

--adding event sponsor 
CREATE OR REPLACE PROCEDURE add_event_sponsor(
    IN p_event_id INT,
    IN p_name TEXT,
    IN p_description TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    
    IF EXISTS (SELECT 1 FROM event WHERE event_id = p_event_id) THEN
       
        INSERT INTO sponsor (name, description, event_id)
        VALUES (p_name, p_description, p_event_id);
    ELSE
        
        RAISE EXCEPTION 'Event with ID % does not exist.', p_event_id;
    END IF;
END;
$$;

--adding event resource 

CREATE OR REPLACE PROCEDURE add_event_resource(
    IN p_event_id INT,
    IN p_name VARCHAR,
    IN p_resource_type VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if the event exists
    IF EXISTS (SELECT 1 FROM event WHERE event_id = p_event_id) THEN
        -- Insert the resource into the table if the event exists
        INSERT INTO resource (resource_name, resource_type, event_id)
        VALUES (p_name, p_resource_type, p_event_id);
    ELSE
        -- Raise an exception if the event does not exist
        RAISE EXCEPTION 'Event with ID % does not exist.', p_event_id;
    END IF;
END;
$$;



-- Create stored procedure to delete a resource
CREATE OR REPLACE PROCEDURE delete_resource(
    IN p_resource_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if the resource exists
    IF EXISTS (SELECT 1 FROM resource WHERE id = p_resource_id) THEN
        
        -- Delete the resource
        DELETE FROM resource WHERE id = p_resource_id;

    ELSE
        -- Raise an exception if the resource does not exist
        RAISE EXCEPTION 'Resource with ID % does not exist.', p_resource_id;
    END IF;
END;
$$;



-- Create stored procedure to delete an event and all associated records
CREATE OR REPLACE PROCEDURE delete_event(
    IN p_event_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if the event exists
    IF EXISTS (SELECT 1 FROM event WHERE event_id = p_event_id) THEN
        
        -- Delete related records from sponsors, resources, and budgets
        DELETE FROM sponsor WHERE event_id = p_event_id;
        DELETE FROM resource WHERE event_id = p_event_id;
        DELETE FROM budget WHERE event_id = p_event_id;

        -- Delete the event itself
        DELETE FROM event WHERE event_id = p_event_id;

    ELSE
        -- Raise an exception if the event does not exist
        RAISE EXCEPTION 'Event with ID % does not exist.', p_event_id;
    END IF;
END;
$$;


-- Create stored procedure to delete a budget
CREATE OR REPLACE PROCEDURE delete_budget(
    IN p_budget_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if the budget exists
    IF EXISTS (SELECT 1 FROM budget WHERE id = p_budget_id) THEN
        
        -- Delete the budget
        DELETE FROM budget WHERE id = p_budget_id;

    ELSE
        -- Raise an exception if the budget does not exist
        RAISE EXCEPTION 'Budget with ID % does not exist.', p_budget_id;
    END IF;
END;
$$;


-- Create stored procedure to delete a sponsor
CREATE OR REPLACE PROCEDURE delete_sponsor(
    IN p_sponsor_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if the sponsor exists
    IF EXISTS (SELECT 1 FROM sponsor WHERE id = p_sponsor_id) THEN
        
        -- Delete the sponsor
        DELETE FROM sponsor WHERE id = p_sponsor_id;

    ELSE
        -- Raise an exception if the sponsor does not exist
        RAISE EXCEPTION 'Sponsor with ID % does not exist.', p_sponsor_id;
    END IF;
END;
$$;


--trigger for deleting an event 
CREATE OR REPLACE FUNCTION log_event_delete_func() 
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO event_log (action, table_name, record_id, change_time)
    VALUES ('DELETE', 'event', OLD.event_id, NOW());
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_event_delete
AFTER DELETE ON event
FOR EACH ROW
EXECUTE FUNCTION log_event_delete_func();


--trigger for adding an event
CREATE OR REPLACE FUNCTION log_event_insert_func() 
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO event_log (action, table_name, record_id, change_time)
    VALUES ('INSERT', 'event', NEW.event_id, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER log_event_insert
AFTER INSERT ON event
FOR EACH ROW
EXECUTE FUNCTION log_event_insert_func();

