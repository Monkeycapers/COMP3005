DROP TRIGGER IF EXISTS auto_email_publisher ON store_items;
--- auto email publisher when quantity falls below auto_order_threshold (for the first time)
CREATE TRIGGER auto_email_publisher
    AFTER UPDATE 
    ON store_items
    FOR EACH ROW
    -- check if old quantity was above the auto_order_threshold so we don't send more emails if quantity drops again
    WHEN ((new.quantity < new.auto_order_threshold) AND old.quantity > old.auto_order_threshold)
    EXECUTE PROCEDURE Email_Publisher();