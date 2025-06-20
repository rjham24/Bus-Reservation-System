# ALL LIBRARIES

import random
#for adding date in format of mm/dd/yyyy
import datetime
People = 0
person_id = []

#connecting mysql to python
import mysql.connector as sqltor # type: ignore
mycon = sqltor.connect(host='localhost', user='root', password='2428', database='ridhima')
if mycon.is_connected():
    print('Successfully Connected to MYSQL database')
else:
    print('Error connecting to MYSQL database')
cursor = mycon.cursor()

#fare prices (global)
FARE_AC = 500
FARE_NON_AC = 300

#will use for the beginning
def Beginning():
    cities = ["Delhi", "Mumbai", "Bengaluru", "Hyderabad", "Manali", "Udaipur", "Rishikesh",
              "Varanasi", "Amritsar", "Chandigarh", "Jaipur", "Lucknow", "Shimla"]
    
    print("\n=== Trip Details ===")
    print("\nThe following are the cities we travel to: " + ", ".join(cities))
    
    while True:
        From = input("\nPlease enter the Departure City : ").title()
        To = input("\nPlease enter the Destination City : ").title()
        
        if From in cities and To in cities:
            break
        else:
            print("Sorry, We don't travel to the mentioned city! Please enter valid cities.")
    
    print("\nTrip booked from", From, "to", To)

    print("\n=== Travel Date ===")
    while True:
        DATE_userInput = input(" Please enter date of travel (MM/DD/YYYY): ").strip()
        try:
            date_obj = datetime.datetime.strptime(DATE_userInput, '%m/%d/%Y').date()
            date = date_obj.strftime('%Y-%m-%d')
            break
        except ValueError:
            print("\nInvalid date format. Please enter again in MM/DD/YYYY format.")

    print("\nTravel confirmed: From", From, "to", To, "on", date)

    cursor.execute("SELECT DISTINCT _FROM FROM Places WHERE _FROM = %s;", (From,))
    data = cursor.fetchall()
    if not data:
        print(" No matching departure city found in database!")
        return
    _FROM = data[0][0]
    print("FROM:", _FROM)

    cursor.execute("SELECT DISTINCT _TO FROM Places WHERE _TO = %s;", (To,))
    data = cursor.fetchall()
    if not data:
        print(" No matching destination city found in database!")
        return
    _TO = data[0][0]
    print("TO:", _TO)

    cursor.execute("SELECT Duration, Distance FROM Places WHERE _FROM = %s AND _TO = %s;", (From, To))
    data = cursor.fetchone()
    if not data:
        print(f"No route found from {From} to {To} in database!")
        return
    DURATION, DISTANCE = data
    print("Duration:", DURATION)
    print("Distance:", DISTANCE)

    def Insertion(i, _FROM, _TO, date, DURATION, DISTANCE):
        query1 = '''INSERT INTO BOOKING (`_FROM`, `_TO`, `DATE`, `DURATION`, `DISTANCE`)
                     VALUES (%s, %s, %s, %s, %s);'''
        cursor.execute(query1, (_FROM, _TO, date, DURATION, DISTANCE))

        query2 = '''UPDATE BOOKING
                    SET PersonID = %s
                    WHERE BookingID = (SELECT LAST_INSERT_ID());'''
        cursor.execute(query2, (person_id[i],))
        mycon.commit()

    Costing(From, To , select_fare_category, People)

    for i in range(People):
        Insertion(i, _FROM, _TO, date, DURATION, DISTANCE)


#will use for adding the details of the passengers

def Passenger_Name_Record():
    global People
    global person_id
    People = int(input(" Enter number of passengers: "))
    for p in range(People):
        print("\n=== Enter Details for Passenger ===")
        First_Name = str(input(" \nFirst Name: "))
        Last_Name = str(input(" \nLast Name: "))
        Age_1 = int(input(" \nAge: "))
        Gender_1 = str(input(" \nMale / Female / Not to specify: "))
        while True:
            PhoneNumber = input("\nMobile Number (10 digits): ")
            if PhoneNumber.isdigit() and len(PhoneNumber) == 10:
                break
            else:
                print("\nInvalid number! Please enter exactly 10 digits.")
        while True:
            Bus_Type = input("\nBus Type (AC / NON-AC): ").strip().upper()
            if Bus_Type in ['AC', 'NON-AC']:
                break
            else:
                print("\nInvalid bus type! Please enter 'AC' or 'NON-AC'.")

        Special_Request = input("\nAny special request (e.g., wheelchair, extra legroom, assistance)? If none, type 'None': ")

        Code = UniqueCode()
        insert = '''INSERT into PassengerNameRecord (First_Name , Last_Name , Age , Gender , PhoneNumber , UniqueCode , Bus_Type , Special_Request)
                    Values ('{}' , '{}' , '{}' , '{}' , '{}' , '{}', '{}', '{}');'''.format(First_Name, Last_Name, Age_1, Gender_1, PhoneNumber, Code, Bus_Type, Special_Request)

        cursor.execute(insert)
        person_id.append(cursor.lastrowid)
        mycon.commit()

    restart = str(input(" \n OOPS! Forget someone?: "))
    if restart in ('y' , 'Y' , 'YES' , 'yes' , 'Yes'):
        Passenger_Name_Record()
    else:
        show = '''SELECT * from passengernamerecord where PersonID in ({}) '''.format(','.join(str(x) for x in person_id))
        cursor.execute(show)
        data = cursor.fetchall()
        for loop in data:
            print(loop)
            

seats = [[None, None, None, None] for _ in range(8)]

def show_seats():
    print("\nBus Seat Layout (None = Available):")
    for i in range(8):
        row_label = f"Row {i+1}:"
        row_data = " | ".join(["Empty" if seat is None else seat for seat in seats[i]])
        print(f"{row_label} {row_data}")

def choose_seat(passenger_name):
    show_seats()
    while True:
        try:
            row = int(input("Enter row number (1 to 8): ")) - 1
            col = int(input("Enter seat number in that row (1 to 4): ")) - 1

            if row < 0 or row >= 8 or col < 0 or col >= 4:
                print("Invalid seat position. Please choose a row between 1-8 and seat between 1-4.")
                continue

            if seats[row][col] is None:
                seats[row][col] = passenger_name
                print("Seat", str(row+1) + "-" + str(col+1), "booked for", passenger_name)
                return str(row + 1) + "-" + str(col + 1)
            else:
                print("That seat is already booked. Please choose another one.")
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

def book_passenger():
    number_of_people = int(input("\nEnter number of passengers: "))
    total_cost = 0

    for _ in range(number_of_people):
        print("\n------ Passenger Details ------")
        first = input("First Name: ")
        last = input("Last Name: ")
        phone = input("Last four digits of Phone Number: ")
        if not (phone.isdigit() and len(phone) == 4):
            print("Invalid Input! Please enter exactly 4 digits.")
            continue
        
        full_name = first + " " + last
        passenger_id = f"{full_name} ({phone})"

        bus_type, fare = select_fare_category()
        print(f"Selected Bus Type: {bus_type}, Fare: Rs {fare}")

        seat_number = choose_seat(passenger_id)
        print("Booking Confirmed for", passenger_id, "at seat", seat_number)
        total_cost += fare

    print(f"\nTotal fare for {number_of_people} passengers is Rs {total_cost}")


def select_fare_category():
    print("Select Bus Type:")
    print("1. AC Bus")
    print("2. Non-AC Bus")
    while True:
        choice = input("Enter choice (1 or 2): ")
        if choice == '1':
            return 'AC', FARE_AC
        elif choice == '2':
            return 'Non-AC', FARE_NON_AC
        else:
            print("Invalid input. Please enter 1 or 2.")



def DeleteRow():
    print(ShowAllPeople())
    input_SerialNumber = int(input("Enter the serial number whose record is to be deleted: "))
    insert2 = '''Delete from PassengerNameRecord where PersonID = '{}' ;'''.format(input_SerialNumber)
    cursor.execute(insert2)
    show = '''Select * from PassengerNameRecord'''
    cursor.execute(show)
    data = cursor.fetchall()
    for loop in data:
        print(loop)
    mycon.commit()


def UpdateRow():
    print(ShowAllPeople())
    SerialNumber = int(input("Enter the Serial Number whose record is to be updated: "))
    First_Name = str(input("\nFirst Name: "))
    Last_Name = str(input("\nLast Name: "))
    Age_1 = int(input("\nAge: "))
    Gender_1 = str(input(" Male / Female / Not to specify: "))
    Special_Request = input("Any special request (e.g., wheelchair, extra legroom, assistance)? If none, type 'None': ")
    while True:
          PhoneNumber = input("Mobile Number (10 digits): ")
          if PhoneNumber.isdigit() and len(PhoneNumber) == 10:
              break
          else:
              print("Invalid number! Please enter exactly 10 digits.")
    Bus_Type = input("Enter Bus Type (AC / NON-AC): ").strip().upper()
    while Bus_Type not in ['AC', 'NON-AC']:
        print(" Invalid bus type! Please enter 'AC' or 'NON-AC'.")
        Bus_Type = input("Enter Bus Type (AC / NON-AC): ").strip().upper()
    insert3 = '''Update PassengerNameRecord
                 Set First_Name = '{}' , Last_Name = '{}' , Age = {} , Gender = '{}' , PhoneNumber = {} , Bus_Type = '{}' ,
                 Special_Request = '{}' where PersonID = {};'''.format(First_Name, Last_Name, Age_1, Gender_1, PhoneNumber, Bus_Type, Special_Request , SerialNumber)
    cursor.execute(insert3)
    show = '''SELECT * from PassengerNameRecord'''
    cursor.execute(show)
    data = cursor.fetchall()
    for loop in data:
        print(loop)
    mycon.commit()

def ShowPlaces():
    cursor.execute("SELECT * from Places;")
    data = cursor.fetchall()
    if not data:
        print("No places found in the database.")
    else:
        print("\n Available Routes:\n")
    for loop in data:
        print(loop)


def ShowCities():
    show_cities = "SELECT DISTINCT _FROM FROM places;"
    cursor.execute(show_cities)
    data = cursor.fetchall()
    count = cursor.rowcount
    
    if not data:
        print("No cities available.")
    else:
        print("\nAvailable Cities:\n")
        for row in data:
            print(">", row[0])
    
    print("Total Number of Cities Retrieved are:", count)


def UniqueCode():
    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = 'ABCDEFGHIJKLMNOPQRSTUVXYZ'
    numbers = '0123456789'
    All = lower + upper + numbers 
    length = 5
    password = "".join(random.sample(All , length))
    return password


def Costing(From, To, select_fare_category, People):
    if From == To:
        print("\nStarting and Ending Destinations cannot be the same!")
        return None

    cities = ["Delhi", "Mumbai", "Bengaluru", "Hyderabad", "Manali", "Udaipur",
              "Rishikesh", "Varanasi", "Amritsar", "Chandigarh", "Jaipur",
              "Lucknow", "Shimla"]

    if From not in cities or To not in cities:
        print("\nWe don’t perform booking in one or both of the mentioned cities!")
        return None

    fare_multipliers = {
        "AC": 1.5,      
        "Non-AC": 1.0   
    }

    if select_fare_category not in fare_multipliers:
        print("\nInvalid fare category selected!")
        return None

    query = "SELECT Distance FROM places WHERE _FROM = '{}' AND _TO = '{}';".format(From, To)

    cursor.execute(query)
    data = cursor.fetchone()

    if data:
        distance = data[0]
        Fixed_Cost = 20
        Per_Km_Cost = 8
        base_cost = Fixed_Cost + distance * Per_Km_Cost
        adjusted_cost = base_cost * fare_multipliers[select_fare_category]
        GST = round(0.09 * adjusted_cost, 2)
        Total_Cost = round(adjusted_cost + GST, 2)

        print("\nYour Total Distance travelled is: " , distance, " km")
        print("Bus Type Selected: " , select_fare_category, " Bus")
        print("Base Cost: " , base_cost)
        print("Adjusted Cost for ", select_fare_category , ":", adjusted_cost)
        print("Tax Applicable: " , GST)
        if  People >= 5:
            discount = 0.20
            discounted_cost = round(Total_Cost * (1 - discount), 2)
            print("Bulk booking detected! 20% discount applied.")
            print("Total Cost after discount (in Rs): " , discounted_cost)
            return discounted_cost
        else:
            print("Total Cost (in Rs): " , Total_Cost)
            return Total_Cost
    else:
        print("Route is not available in the database")
        return None
    

def CancelBookingAndRefund():
    full_name = input("Enter the full name used for booking: ").strip()
    phone = input("Enter the phone number used for booking: ").strip()

    if not phone.isdigit():
        print("Invalid phone number format.")
        return

    # Search for the booking
    cursor.execute("""
        SELECT BookingID, Name, Phone, PaymentMethod, TotalCost
        FROM BOOKING
        WHERE LOWER(Name) = %s AND Phone = %s
    """, (full_name.lower(), phone))
    
    result = cursor.fetchone()

    if result:
        booking_id, name, phone, payment_method, amount = result
        confirm = input(f"\nBooking found: {name} ({phone}), Paid ₹{amount} via {payment_method}.\nDo you want to cancel and proceed with refund? (yes/no): ").lower()

        if confirm == 'yes':
            # Refund logic
            if payment_method.lower() in ['upi', '3']:
                print("Refund will be processed to your UPI account within 1–2 business days.")
            elif payment_method.lower() in ['credit card', '1', 'debit card', '2']:
                print("Refund will be credited to your card within 3–5 business days.")
            elif payment_method.lower() in ['cash on delivery', '5']:
                print("Refund to be collected in person at the booking counter.")
            else:
                print("Unknown payment method. Refund may be delayed.")

            # Delete the record
            cursor.execute("DELETE FROM BOOKING WHERE BookingID = %s", (booking_id,))
            mycon.commit()
            print("\nYour booking has been cancelled and refund initiated.\n")
        else:
            print("Cancellation aborted.")
    else:
        print("No booking found with the given details.")


def ShowAllPeople():
    show = '''SELECT * from PassengerNameRecord'''
    cursor.execute(show)
    data = cursor.fetchall()
    for loop in data:
        print(loop)

def ShowAllBookings():
    query = "SELECT * FROM BOOKING;"
    cursor.execute(query)
    data = cursor.fetchall()
    if not data:
        print("No bookings found.")
    else:
        print("\nCurrent Booking Records:\n")
        for row in data:
            print(row)


def DeleteRow_Booking():
    ShowAllBookings()
    input_SerialNumber = int(input("Enter the BookingID whose record is to be deleted: "))
    delete_query = '''DELETE FROM BOOKING WHERE BookingID = {};'''.format(input_SerialNumber)
    cursor.execute(delete_query)
    mycon.commit()
    print("\nRecord deleted successfully.\n")
    ShowAllBookings()


def UpdateRow_Booking():
    print(ShowAllBookings())
    BookingID = int(input("Enter the BookingID whose record has to be updated"))
    From = input("Enter the Departure City: ").upper()
    To = input("Enter the Destination City: ").upper()
    DATE_userInput = input("Please enter date of travel (MM/DD/YYYY): ")
    date = datetime.datetime.strptime(DATE_userInput, '%m/%d/%Y').date().strftime('%m/%d/%Y')
    cities = ["Delhi", "Mumbai", "Bengaluru", "Hyderabad", "Manali", "Udaipur", "Rishikesh", "Varanasi", "Amritsar", "Chandigarh", "Jaipur", "Lucknow", "Shimla"]
    if From not in cities and To not in cities:
        print("Sorry , we dont travel to that city. change your destination.")
        print(UpdateRow_Booking())
    else:
        show1 = "SELECT DISTINCT _FROM FROM places WHERE _FROM = '{From}';"
        show2 = "SELECT DISTINCT _TO FROM places WHERE _TO = '{To}';"
        show3 = "SELECT Duration FROM places WHERE _FROM = '{From}' AND _TO = '{To}';"
        show4 = "SELECT Distance FROM places WHERE _FROM = '{From}' AND _TO = '{To}';"
        cursor.execute(show1)
        data = cursor.fetchall()
        for loop in data:
            print("From     :", loop[0])
            _FROM = loop[0]
            
        cursor.execute(show2)
        data = cursor.fetchall()
        for loop in data:
            print("To       :", loop[0])
            _TO = loop[0]

        cursor.execute(show3)
        data = cursor.fetchall()
        for loop in data:
            print("Duration :", loop[0])
            DURATION = loop[0]

        cursor.execute(show4)
        data = cursor.fetchall()
        for loop in data:
            print("Distance :", loop[0])
            DISTANCE = loop[0]

    update_query = '''UPDATE Booking
                      SET _FROM = %s, _TO = %s, DATE = %s, DURATION = %s, DISTANCE = %s
                      WHERE BookingID = %s;'''
    cursor.execute(update_query, (_FROM, _TO, date, DURATION, DISTANCE, BookingID))
    mycon.commit()

    show = '''SELECT * from Booking'''
    cursor.execute(show)
    data = cursor.fetchall()
    for loop in data:
        print(loop)


def choose_payment_method():
    print("\nChoose your payment method:")
    print("1. Credit Card")
    print("2. Debit Card")
    print("3. UPI")
    print("4. Net Banking")
    print("5. Cash on Delivery")

    while True:
        choice = input("Enter option number (1-5): ")
        if choice == '1':
            print("You selected Credit Card.")
            bank = input("Enter your Bank Name : ")
            last4 = input("Enter last 4 digits of your Credit Card Number: ")
            cname = input("Enter Cardholder Name: ")
            print("Processing payment with" , bank, " Credit Card ending in", last4)
            break

            break
        elif choice == '2':
            print("You selected Debit Card.")
            bank = input("Enter your Bank Name : ")
            last4 = input("Enter last 4 digits of your Debit Card Number: ")
            cname = input("Enter Cardholder Name: ")
            print("Processing payment with" , bank, " Debit Card ending in", last4)
            break
  
            break
        elif choice == '3':
            print("You selected UPI.")
            upi_id = input("Enter your UPI ID: ")
            print(f"UPI ID {upi_id} received.")
            break
        elif choice == '4':
            print("You selected Net Banking.")
            bank = input("Enter your Bank Name: ")
            print("Redirecting to " , bank, " Net Banking portal.")
            break

            break
        elif choice == '5':
            print("You selected Cash on Delivery. Please pay cash to the conductor on board.")
            break
        
        else:
            print("Invalid option, please select again.")

    print("Payment method confirmed. Thank you for your payment!")
    return choice


def assign_travel_time_based_on_class(bus_class):
    print("\nChoose travel time:")
    print("1. Day Travel")
    print("2. Night Travel")

    day_times = ["7:00 AM", "9:00 AM", "11:00 AM", "1:00 PM", "3:00 PM", "5:00 PM"]
    night_times = ["7:00 PM", "9:00 PM", "11:00 PM", "1:00 AM", "3:00 AM", "5:00 AM"]

    while True:
        choice = input("Enter 1 for Day or 2 for Night: ")
        if choice == '1':
            time_label = "Day"
            dep_time = random.choice(day_times)
            break
        elif choice == '2':
            time_label = "Night"
            dep_time = random.choice(night_times)
            break
        else:
            print("Invalid input. Please enter 1 or 2.")

    print(f"\nYou selected {time_label} travel with {bus_class} bus.")
    print(f"Departure Time: {dep_time}")

    return time_label, dep_time


def choose_meal():
    print("\nMeal Preferences:")
    print("1. Veg Meal ")
    print("2. Non-Veg Meal ")
    print("3. Jain Meal ")
    print("4. No Meal ")

    while True:
        meal_choice = input("Select your meal option (1–4): ")
        if meal_choice == '1':
            return "Veg Meal"
        elif meal_choice == '2':
            return "Non-Veg Meal"
        elif meal_choice == '3':
            return "Jain Meal"
        elif meal_choice == '4':
            return "No Meal"
        else:
            print("Invalid input. Please choose between 1 and 4.")



def collect_feedback():
    print("\nWe value your feedback!")
    passenger = input("Enter your name: ")
    
    while True:
        try:
            rating = int(input("Please rate your experience (1 to 5 stars): "))
            if 1 <= rating <= 5:
                break
            else:
                print("Rating must be between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5.")

    comments = input("Any comments or suggestions (optional): ")

    insert_feedback = '''INSERT INTO Feedback (PassengerName, Rating, Comments)
                         VALUES (%s, %s, %s);'''
    cursor.execute(insert_feedback, (passenger, rating, comments))
    mycon.commit()
    
    print("Thank you for your feedback!")


# MAIN PROGRAM

print(40 * 'X-')
print("\n")
print("WELCOME TO BUS RESERVATION APPLICATION".upper().center(50, '*'))
print("1. Open Customer Services")
print("2. Open Admin Mode")
CheckUser = int(input("Enter the number to open a Mode: "))
print("\n")

if CheckUser == 1:
    print(80 * '#')
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        print("\nGood Morning!")
    elif current_hour < 18:
        print("\nGood Afternoon!")
    else:
        print("\nGood Evening!")
    print("\nGreetings of the Day")
    print("\nOur Buses provide Travel Services to various Metropolitan Cities in India on a daily basis: ")
    ShowCities()
    print("\n")
    print("\nWe provide 2 types of buses for our passengers: AC Class and NON-AC Class ")
    print('''\nExtra facilities we provide for your comfort:
\n=> Complimentary Snacks & Beverages
\n=> On-board Entertainment and WiFi
\n=> Live GPS Tracking for your journey
\n=> Charging Ports at Every Seat
\n=> Blankets & Pillows for longer trips
\n=> Priority Boarding for Seniors and Differently-Abled
\n=> Clean and Hygienic Restrooms
\n=> Friendly and Trained Staff on board
\n=> Contactless Payment Options
\n=> Emergency Medical Kit & First Aid''')
    print("\n")
    print("We are happy to serve you with our services. Please proceed to book your tickets.")
    print("\n")

    while True:
        print("\n--- Customer Menu ---")
        print("1. Book Ticket")
        print("2. Show All Bookings")
        print("3. Cancel Booking and Refund")
        print("4. Exit Customer Services")

        choice = input("Enter your choice: ")

        if choice == '1':
            Passenger_Name_Record()
            print("\nWELCOME TO SIMPLE BUS SEAT BOOKING")
            book_passenger()
            print("\nAll bookings complete. Final seat chart: ")
            show_seats()
            print("\nWhere would you like to go? ")
            Beginning()

            meal_pref = choose_meal()

            bus_class = input("Enter bus class (AC/NON-AC): ").upper()
            travel_pref, dep_time = assign_travel_time_based_on_class(bus_class)

            payment_method = choose_payment_method()

            cursor.execute("SELECT * FROM booking ORDER BY BookingID DESC LIMIT %s", (People,))
            latest_bookings = cursor.fetchall()
            cursor.execute("SELECT First_Name FROM PassengerNameRecord ORDER BY PersonID DESC LIMIT %s", (People,))
            latest_names = cursor.fetchall()

            print("\nINDIVIDUAL BOOKING SUMMARIES")
            print("=" * 40)
            for i in range(People):
                booking = latest_bookings[i]
                name = latest_names[i][0]
                
                print(f"\nPassenger {i+1}")
                print("=" * 40)
                print(f"Name            : {name}")
                print(f"Booking ID      : {booking[0]}")
                print(f"From            : {booking[1]}")
                print(f"To              : {booking[2]}")
                print(f"Date of Travel  : {booking[3]}")
                print(f"Duration        : {booking[4]}")
                print(f"Distance        : {booking[5]}")
                print(f"Bus Class       : {booking[6]}")
                print(f"Seat Number     : {booking[7]}")
                print(f"Amount Paid     : ₹{booking[8]}")
                print(f"Payment Method  : {payment_method}")
                print(f"Meal Preference : {meal_pref}")
                print(f"Travel Time Pref.    : {travel_pref}")
                print(f"Departure Time       : {dep_time}")
                print("-" * 40)

            print("\nThank You , We are giving you a registration code. Use this for further reference")
            code = UniqueCode()
            print("Your Unique Booking Code:", code)
            collect_feedback()

        elif choice == '2':
            ShowAllBookings()

        elif choice == '3':
            CancelBookingAndRefund()

        elif choice == '4':
            print("Exiting Customer Services...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

elif CheckUser == 2:
    print(40 * 'X-')
    print("\n")
    password = input("\nEnter password to continue: ")
    count = 0
    while count < 3:
        if password.lower() == 'admin':
            print("\nAccess Granted")
            break
        else:
            print("\nAccess Denied. Try Again.")
            count += 1
            if count >= 3:
                print("Too many failed attempts. Exiting.")
                exit()

    print(80 * '#')

    def MENU():
        print("\nMENU")
        print("1. Add a passenger (Passenger_Name_Record)")
        print("2. Update a record of the passenger (Passenger_Name_Record)")
        print("3. Delete a record of the passenger (Passenger_Name_Record)")
        print("4. Update a record of the passenger (BOOKING)")
        print("5. Delete a record of the passenger (BOOKING)")
        print("6. Exit Admin Menu")

        Input1 = int(input("Enter the number from the Menu to proceed: "))
        if Input1 == 1:
            Passenger_Name_Record()
            MENU()
        elif Input1 == 2:
            UpdateRow()
            MENU()
        elif Input1 == 3:
            DeleteRow()
            MENU()
        elif Input1 == 4:
            UpdateRow_Booking()
            MENU()
        elif Input1 == 5:
            DeleteRow_Booking()
            MENU()
        elif Input1 == 6:
            print("Exiting Admin Menu.")
            exit()
        else:
            print("Invalid input. Try again.")
            MENU()

    MENU() 