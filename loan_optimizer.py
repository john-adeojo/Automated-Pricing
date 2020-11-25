import pandas as pd
import numpy as np





class LoanInstance():

    def __init__(self,
                 amount=0,
                 term=0,
                 apr=0,
                 score=0,
                 balance_profile_end=[],
                 balance_profile_start=[],
                 interest_profile=[],
                 recieved_interest=[],
                 recieved_capital=[],
                 cohort_interest_profile=[],
                 write_off_curves=[],
                 cohort={},
                 price_args=np.array([]),
                 write_off=np.array([]),
                 total_interest=0
                 ):

        self.amount = amount
        self.term = term
        self.apr = apr
        self.score = score
        self.cohort = cohort
        self.price_args = price_args
        self.total_interest = total_interest

        self.balance_profile_start = balance_profile_start  # Starting balance profile over loan term
        self.balance_profile_end = balance_profile_end  # End balance profile over loan term
        self.interest_profile = interest_profile  # Interest accrued over loan term
        self.recieved_interest = recieved_interest  # Recieved interest profile
        self.recieved_capital = recieved_capital  # Recieved capital profile
        self.cohort_interest_profile = cohort_interest_profile  # Interest profile over entire loan cohort
        self.write_off_curves = write_off_curves  # All modelled write-off curves
        self.write_off = write_off  # Write off profile for a given loan

    # Read in loan cohort and write offs from csv
    def read_cohort(self, location_cohort, location_wo):
        self.cohort = pd.read_csv(location_cohort)
        self.write_off_curves = pd.read_csv(location_wo)
        arr = self.price_args
        self.price_args = np.append(arr, np.array(self.cohort['apr']))  # returns the apr as an 1d array for apr

    # Generate repayment profiles

    def repayment_profiles(self, arg):

        # Reset all profiles to blank for optimisation purposes
        self.cohort_interest_profile = []
        self.balance_profile_start = []
        self.balance_profile_end = []
        self.interest_profile = []

        # iterate over the number of loans in the cohort
        for row in range(0, len(self.cohort)):

            # Initialise the balance profiles at start of every loop
            balance_profile_end = []
            balance_profile_start = []
            interest_profile = []

            # Assign loan attributes from the loans cohort
            self.term = self.cohort.at[row, 'term']
            self.apr = arg[
                row]  # Score and trm adjustments added to apr to ensure high score and long terms have lower APRs than low score and low terms
            self.score = self.cohort.at[row, 'score']

            # Faux model to estimate booking probability should be replaced by data driven model
            booking_prob = 1 - arg[row]

            # Generate write-off profile
            self.write_off = np.array(self.write_off_curves[self.score])

            # Interest income is proportional to amount
            self.amount = (self.cohort.at[
                               row, 'amount'] * booking_prob)  # Loan amount adjusted by probability of booking a loan

            # initialise loan term to loop over
            loanterm = range(0, self.term + 1)
            # n = self.term/12  # Repayment term in years

            nominal_interest = (((self.apr + 1) ** (
                        1 / 12)) - 1) * 12  # Nominal interest rate: APR excluding other fees
            monthly_rate = nominal_interest / 12  # Monthly customer rate

            monthly_repayment = (self.amount * monthly_rate) / (
                        1 - (1 + (monthly_rate)) ** (-self.term))  # Fixed monthly repayment

            # Generate contractual repayment over the term of the loan
            for month in loanterm:  # Set special case for month 0
                if month == 0:

                    interest = recieved_int = 0
                    recieved_capital = 0
                    balance_start = 0  # Gives a starting balance profile of 0 at month 0
                    default_balance = self.write_off[0]
                    balance_end = self.amount - default_balance

                    self.interest_profile.append(interest)  # Append interest to interest profile
                    self.balance_profile_end.append(balance_end)  # Append balance to balance profile end
                    self.balance_profile_start.append(balance_start)  # Append balance to balance profile start


                elif month == 1:  # set special case for month 1

                    balance_start = self.amount
                    self.balance_profile_start.append(balance_start)

                    interest = monthly_rate * self.balance_profile_start[1]
                    self.interest_profile.append(interest)

                    default_balance = self.write_off[1] * balance_start

                    balance_end = self.balance_profile_start[1] + self.interest_profile[
                        1] - monthly_repayment - default_balance
                    self.balance_profile_end.append(balance_end)

                    # print(month)

                else:

                    balance_start = self.balance_profile_end[month - 1]
                    self.balance_profile_start.append(balance_start)

                    interest = monthly_rate * self.balance_profile_start[month]
                    self.interest_profile.append(interest)

                    default_balance = self.write_off[month] * balance_start

                    balance_end = self.balance_profile_start[month] + self.interest_profile[
                        month] - monthly_repayment - default_balance
                    self.balance_profile_end.append(balance_end)

        # Append all interest profiles to gt interest profile for the entire cohort
        self.cohort_interest_profile.append(self.interest_profile)
        # Calculate total interest income for cohort
        self.total_interest = np.sum(np.array(self.cohort_interest_profile)) * -1

        return self.total_interest

if __name__ == "__main__":
    print('Starting optimization process')
    # Run optimatisation over loan cohort
    from scipy.optimize import minimize
    import time

    # Create a loans object here by reading in loans data
    print('Creating a loan instance object')
    loans = LoanInstance()
    print('Loading cohorts: loans_test3.csv and write-off.csv')
    loans.read_cohort(r"loans_test3.csv",
                      r"write-off.csv")  # Import the loan cohort into the loan object

    # Set up the objective function
    x0 = loans.price_args

    objective_function = lambda x: (loans.repayment_profiles(x))

    # Bounds set up
    lw = [0.145] * (len(loans.cohort))
    up = [0.355] * (len(loans.cohort))
    bounds = list(zip(lw, up))

    start_time = time.process_time()
    print('Running optimisation')
    optimum_price = minimize(objective_function, x0, bounds=bounds, method='Powell',
                             options={'maxiter': 10000, 'disp': True})

    # Record time taken to run optimisation
    print(time.process_time() - start_time, "Seconds")
    data = loans.cohort
    data['optimum_apr'] = optimum_price.x
    print('Printing optimum pricing strategy')
    print(data.drop(columns=['Unnamed: 4', 'Unnamed: 5',  'Unnamed: 6',  'Unnamed: 7', 'Unnamed: 8']))
