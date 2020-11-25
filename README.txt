--- Project Overview ---
# Overview
This project runs a price optimisation on a cohort of 38 consumer credit loans defined by the loan amount, credit score, apr and term.  The optimisation aims to maximise the interest income generated across the lending cohort by varying the pricing (apr). 
Pricing (apr) for loans is between 0.145 and 0.355. 

# Data 
wrte-off.csv -> write off profiles as a percentage of balance each month according to risk score tier
loans_test3.csv -> loan cohort data 
Note: All data is fictional and just for the purposes of testing the optimisation strategy

# Method 
A balance repayment profile is generated for each loan. The objective function then becomes the negative sum of the interest income across the entire loan cohort.
A ‘faux’ demand model is in-place that calculates a probability of booking a loan as (1-apr). essentially higher priced loans have a reduced probability of booking than lower priced ones.

SciPY’s minimization algorithm is applied to the objective function to find the optimum pricing using the Powell method -> https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html

--- Outputs ---
The code outputs an optimal strategy as delivered by the optimisation method.
*Current function value* is the interest income across the entire loan cohort.


# Considerations 
The objective function is currently using nested for loops which is O(n^2) in computational steps. Can this be done more efficiently? 
Is there a better method for optimising interest income across the cohort? 


---How to run ---

Step 1 - Navigate to folder directory storing this project in your command prompt
Step 2 - Run the commands below in your command prompt.
 
py -m venv env
.\env\Scripts\activate
pip install requirements.txt
python loan_optimizer.py
