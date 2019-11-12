# Time_Table_Creator

This is the project for creating a Time Table Creator. It is for IIT Goa Logic Course.

## Steps to use the file

The file uses time.json as the input. It will work for any input given it is in the format of the time.json file.

To use it

- Enter your input in time.json
- Run the command `python time_table.py`

## How is it working

The problem is a typical example of CSP. In the constraint satisfaction problem, we are using forward checking and backtracking, for assigning the best possible solution.

We have used z3 to see that the final assignment which has been assigned by forward checking is possible or not.

## Team

The project was made by Muskan Jain(170010018) and Rahul Kashyap(170010027).
