CREATE TABLE users (
    id integer generated by default as identity primary key,
    email varchar(255),
    pw_hash varchar(255)
);