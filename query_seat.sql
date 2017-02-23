﻿CREATE TABLE seat
(username BIGINT PRIMARY KEY,
password CHARACTER VARYING(30) NOT NULL,
seat int NOT NULL,
start_time int NOT NULL,
end_time int NOT NULL
);

SELECT seat,start_time,end_time FROM seat WHERE username=2014301130041;