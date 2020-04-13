DROP FUNCTION IF EXISTS public.Email_Publisher;

CREATE FUNCTION Email_Publisher()
    RETURNS trigger
    LANGUAGE 'plpgsql'
AS $BODY$-- We email the publisher requesting more quantity
DECLARE publisher_id numeric;
BEGIN
SELECT book.publisher_id INTO publisher_id FROM store_items FULL OUTER JOIN book ON store_items.ref_id=book.id WHERE store_items.id=new.id;
--- to showcase just put the amount and the publisher id in email_request table
INSERT INTO email_request SELECT SUM(store_item_history.amount), publisher_id, 'now' FROM store_item_history
FULL OUTER JOIN orders ON store_item_history.order_id=orders.id
WHERE store_item_history.store_item_id=new.id AND orders.order_date BETWEEN SYMMETRIC now() - interval '1 month' AND now();
--- email with that amount... not implemented but this is where we would interface with the emailing component
RETURN new;
END;$BODY$;


--- make sure postgres owns it
ALTER FUNCTION Email_Publisher()
    OWNER TO postgres;