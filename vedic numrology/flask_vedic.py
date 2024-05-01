from flask import Flask, render_template, request
from datetime import datetime, timedelta
import logging

# Set up Flask app
app = Flask(__name__)

# Set up logging    
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Dictionaries for month and weekday conversion
month_to_number = {
    'January': 1, '1': 1,
    'February': 2, '2': 2,
    'March': 3, '3': 3,
    'April': 4, '4': 4,
    'May': 5, '5': 5,
    'June': 6, '6': 6,
    'July': 7, '7': 7,
    'August': 8, '8': 8,
    'September': 9, '9': 9,
    'October': 10, '10': 10,
    'November': 11, '11': 11,
    'December': 12, '12': 12
}

weekday_to_number = {'Monday': 2, 'Tuesday': 9, 'Wednesday': 5, 'Thursday': 3,
                     'Friday': 6, 'Saturday': 8, 'Sunday': 1}

# Cycles and their respective names
cycles = {1: 'surya', 2: 'chandra', 3: 'brihaspati', 4: 'rahu', 5: 'budh', 6: 'shukra', 7: 'ketu', 8: 'shani', 9: 'mangal'}

# Helper function to sum digits
def sum_digits(n):
    return sum(int(d) for d in str(n))

# Calculation functions
def calculate_basic_number(day):
    result = sum_digits(day)
    # Cycle back to 1 after reaching 9
    while result > 9:
        result -= 9
    logging.info(f"Calculated Basic Number: {result}")
    return result

def calculate_destiny_number(day, month, year):
    total = sum_digits(day) + sum_digits(month) + sum_digits(year)
    while total >= 10:
        total = sum_digits(total)
    logging.info(f"Calculated Destiny Number: {total}")
    return total

def calculate_maha_dasha(birth_year, basic_number, target_year):
    maha_dasha_year = birth_year
    maha_dasha_number = basic_number

    # Start calculating the Maha Dasha years
    while True:
        # Calculate the next Maha Dasha year
        maha_dasha_year += maha_dasha_number

        # Check if the next Maha Dasha year exceeds the target year
        if maha_dasha_year > target_year:
            # Since it exceeds, we found our Maha Dasha year, so we break the loop
            break

        # Increment the Maha Dasha number or reset to 1 if it was 9
        maha_dasha_number = 1 if maha_dasha_number == 9 else maha_dasha_number + 1

    # Log the final Maha Dasha year and number
    logging.info(f"Final Calculated Maha Dasha year: {maha_dasha_year}")
    logging.info(f"Final Calculated Maha Dasha number: {maha_dasha_number}")

    return maha_dasha_year, maha_dasha_number

def calculate_antar_dasha(birth_month, basic_number, target_year_last_two_digits, weekday_number):
    total = birth_month + basic_number + target_year_last_two_digits + weekday_number
    while total >= 10:
        total = sum_digits(total)
    logging.info(f"Calculated Antar Dasha Number: {total}")
    return total

def calculate_pratyantar_dasha(antar_dasha, current_date):
    multiplier = 8
    start_cycle_index = antar_dasha
    results = []
    start_date = current_date

    for i in range(9):
        cycle_index = (start_cycle_index + i - 1) % 9 + 1
        cycle_name = cycles[cycle_index]
        days_in_cycle = cycle_index * multiplier
        end_date = start_date + timedelta(days=days_in_cycle - 1)
        results.append((cycle_name, start_date.strftime('%d %b %Y'), end_date.strftime('%d %b %Y')))
        start_date = end_date + timedelta(days=1)

    # Adjust the last cycle's end date by adding 5 more days
    last_cycle = results[-1]
    last_end_date = datetime.strptime(last_cycle[2], '%d %b %Y') + timedelta(days=5)
    results[-1] = (last_cycle[0], last_cycle[1], last_end_date.strftime('%d %b %Y'))

    return results

# Helper function to create the Vedic Natal Grid based on the birthdate
def create_vedic_natal_grid(birthdate, basic_number, destiny_number):
    # Convert birthdate to MMDDYY format for easy parsing, ignoring the century part of the year
    numbers = ''.join(filter(str.isdigit, birthdate.strftime('%m%d%y')))
    grid_counts = {str(i): numbers.count(str(i)) for i in range(1, 10)}
    
    # Add basic and destiny numbers to their counts
    grid_counts[str(basic_number)] = grid_counts.get(str(basic_number), 0) + 1
    grid_counts[str(destiny_number)] = grid_counts.get(str(destiny_number), 0) + 1

    # If the day ends in 0, replace the count for that number with 1
    day_str = str(birthdate.day)
    if day_str.endswith('0'):
        grid_counts[day_str[0]] = 1  # Set count for that specific number to 1

    # Define the positions in the grid (from the example grid structure)
    grid_positions = [
        [str(3) * grid_counts.get('3', 0), str(1) * grid_counts.get('1', 0), str(9) * grid_counts.get('9', 0)],
        [str(6) * grid_counts.get('6', 0), str(7) * grid_counts.get('7', 0), str(5) * grid_counts.get('5', 0)],
        [str(2) * grid_counts.get('2', 0), str(8) * grid_counts.get('8', 0), str(4) * grid_counts.get('4', 0)]
    ]

    return grid_positions


def create_maha_antar_dasha_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha_number):
    # Convert birthdate to MMDDYY format for easy parsing, ignoring the century part of the year
    numbers = ''.join(filter(str.isdigit, birthdate.strftime('%m%d%y')))
    grid_counts = {str(i): numbers.count(str(i)) for i in range(1, 10)}
    
    # Add basic and destiny numbers to their counts
    grid_counts[str(basic_number)] = grid_counts.get(str(basic_number), 0) + 1
    grid_counts[str(destiny_number)] = grid_counts.get(str(destiny_number), 0) + 1

    # If the day ends in 0, replace the count for that number with 1
    day_str = str(birthdate.day)
    if day_str.endswith('0'):
        grid_counts[day_str[0]] = 1  # Set count for that specific number to 1

    # Add Maha Dasha and Antar Dasha numbers to their counts
    grid_counts[str(maha_dasha_number)] = grid_counts.get(str(maha_dasha_number), 0) + 1
    grid_counts[str(antar_dasha_number)] = grid_counts.get(str(antar_dasha_number), 0) + 1

    # Now the grid includes counts of Maha Dasha and Antar Dasha numbers as well
    grid_positions = [
        [str(3) * grid_counts.get('3', 0), str(1) * grid_counts.get('1', 0), str(9) * grid_counts.get('9', 0)],
        [str(6) * grid_counts.get('6', 0), str(7) * grid_counts.get('7', 0), str(5) * grid_counts.get('5', 0)],
        [str(2) * grid_counts.get('2', 0), str(8) * grid_counts.get('8', 0), str(4) * grid_counts.get('4', 0)]
    ]

    return grid_positions


def create_cycle_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha_number, cycle_adjustments):
    numbers = ''.join(filter(str.isdigit, birthdate.strftime('%m%d%y')))
    grid_counts = {str(i): numbers.count(str(i)) for i in range(1, 10)}
    
    # Add counts for Basic, Destiny, Maha Dasha, and Antar Dasha numbers
    grid_counts[str(basic_number)] += 1
    grid_counts[str(destiny_number)] += 1
    grid_counts[str(maha_dasha_number)] += 1
    grid_counts[str(antar_dasha_number)] += 1

    # Apply the specific cycle adjustments
    for number, count in cycle_adjustments.items():
        grid_counts[number] = grid_counts.get(number, 0) + count

    # Construct the grid
    grid_positions = [
        [str(3) * grid_counts.get('3', 0), str(1) * grid_counts.get('1', 0), str(9) * grid_counts.get('9', 0)],
        [str(6) * grid_counts.get('6', 0), str(7) * grid_counts.get('7', 0), str(5) * grid_counts.get('5', 0)],
        [str(2) * grid_counts.get('2', 0), str(8) * grid_counts.get('8', 0), str(4) * grid_counts.get('4', 0)]
    ]

    return grid_positions




@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    results = None
    birthdate_input = ''
    target_year_input = ''
    vedic_natal_grid = None  # Initialize vedic_natal_grid to None at the start
    maha_antar_dasha_grid = None  # Add this line to initialize maha_antar_dasha_grid

    if request.method == 'POST':
        birthdate_input = request.form.get('birthdate')
        target_year_input = request.form.get('target_year')

        # Parse the input data and run calculations
        try:
            # Split the input into components
            birthdate_parts = birthdate_input.split()
            day_part = birthdate_parts[0]
            month_part = birthdate_parts[1].capitalize()
            year_part = birthdate_parts[2]

            # Determine if the month is a number or a name and convert to number
            month = month_to_number.get(month_part, month_part)
            if isinstance(month, str) and month.isdigit():
                month = int(month)

            # Reconstruct the birthdate string for parsing
            birthdate_str = f"{day_part} {month} {year_part}"
            birthdate = datetime.strptime(birthdate_str, "%d %m %Y")

            day = birthdate.day
            year = birthdate.year
            target_year = int(target_year_input)

            if target_year < year:
                raise ValueError("Target year must be greater than or equal to birth year.")

            # Perform all calculations
            basic_number = calculate_basic_number(day)
            destiny_number = calculate_destiny_number(day, month, year)
            maha_dasha_year, maha_dasha_number = calculate_maha_dasha(year, basic_number, target_year)
            current_date_same_year = datetime(target_year, month, day)
            weekday_number = weekday_to_number[current_date_same_year.strftime('%A')]
            antar_dasha = calculate_antar_dasha(month, basic_number, int(str(target_year)[-2:]), weekday_number)
            pratyantar_dasha_results = calculate_pratyantar_dasha(antar_dasha, current_date_same_year)

            # Now vedic_natal_grid will have a value or remain None if an exception occurs
            vedic_natal_grid = create_vedic_natal_grid(birthdate, basic_number, destiny_number)

            # Inside your index function, after calculating Maha Dasha and Antar Dasha numbers
            maha_antar_dasha_grid = create_maha_antar_dasha_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha)

            # For Budh cycle grid
            budh_adjustments = {'5': 1}
            budh_grid = create_cycle_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha, budh_adjustments)

            # For Shukra cycle grid
            shukra_adjustments = {'6': 1}
            shukra_grid = create_cycle_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha, shukra_adjustments)

            # For Ketu cycle grid
            ketu_adjustments = {'7': 1}
            ketu_grid = create_cycle_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha, ketu_adjustments)

            # For Shani cycle grid
            shani_adjustments = {'8': 1}
            shani_grid = create_cycle_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha, shani_adjustments)

            # For Mangal cycle grid
            mangal_adjustments = {'9': 1}
            mangal_grid = create_cycle_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha, mangal_adjustments)

            # For Surya cycle grid
            surya_adjustments = {'1': 1}
            surya_grid = create_cycle_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha, surya_adjustments)

            # For Chandra cycle grid
            chandra_adjustments = {'2': 1}
            chandra_grid = create_cycle_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha, chandra_adjustments)

            # For Brihaspati cycle grid
            brihaspati_adjustments = {'3': 1}
            brihaspati_grid = create_cycle_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha, brihaspati_adjustments)

            # For Rahu cycle grid
            rahu_adjustments = {'4': 1}
            rahu_grid = create_cycle_grid(birthdate, basic_number, destiny_number, maha_dasha_number, antar_dasha, rahu_adjustments)

            # Prepare results to be displayed on the web page
            results = {
                "Basic Number": basic_number,
                "Destiny Number": destiny_number,
                "Maha Dasha Year": maha_dasha_year,
                "Maha Dasha Number": maha_dasha_number,
                "Antar Dasha Number": antar_dasha,
                "Pratyantar Dasha": pratyantar_dasha_results,
                "Budh Grid": budh_grid,
                "Shukra Grid": shukra_grid,
                "Ketu Grid": ketu_grid,
                "Shani Grid": shani_grid,
                "Mangal Grid": mangal_grid,
                "Surya Grid": surya_grid,
                "Chandra Grid": chandra_grid,
                "Brihaspati Grid": brihaspati_grid,
                "Rahu Grid": rahu_grid
            }

        except ValueError as e:
            error = str(e)
            maha_antar_dasha_grid = None
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            error = "An unexpected error occurred."
            maha_antar_dasha_grid = None

    # Whether it's GET or POST, render the index.html with appropriate context
    return render_template('index.html', error=error, results=results, 
                           birthdate_input=birthdate_input, target_year_input=target_year_input, 
                           vedic_natal_grid=vedic_natal_grid, maha_antar_dasha_grid=maha_antar_dasha_grid)

if __name__ == '__main__':
    app.run(debug=True)