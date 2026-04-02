SET SCHEMA JESSEG;

-- Create the function if it doesn't exist
CREATE OR REPLACE FUNCTION JESSEG.THREESAT()
  RETURNS TABLE (c1 INT, c2 INT, c3 INT, c4 INT)
  LANGUAGE SQL
  SPECIFIC JESSEG.THREESAT
  NOT DETERMINISTIC
  NO EXTERNAL ACTION
  RETURN
    VALUES (-1, -2, -3, 0),
           ( 1, -2,  3, 0),
           ( 1,  2, -3, 0),
           ( 1, -2, -3, 0),
           (-1,  2,  3, 0);

SELECT * FROM TABLE(JESSEG.THREESAT()) AS t;