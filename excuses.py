import sqlite3

def create_database():
    conn = sqlite3.connect('excuses.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_excuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            excuse TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goout_excuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            excuse TEXT NOT NULL
        )
    ''')

    # Insert 20 excuses into work_excuses table
    work_excuses = [
       "My laptop crashed and I lost all my progress", "The Wi-Fi went out and I couldn't access the online resources",
       "I thought the assignment was due next week", "I had to finish a critical project for another class/job", "I forgot my homework at home",
       "I've been sick and couldn't focus on the assignment", "I was waiting for my group member to send their part",
       "A personal issue came up and I was unable to concentrate", "I wasn't clear on the assignment details and didn't want to do it wrong",
         "A family member was hospitalized and I had to be there", "I had a severe migraine and couldn't work",
           "My pet got sick and I had to take them to the vet", "I had to run emergency errands for my family",
           "I had a last-minute doctor's appointment", "An unexpected guest arrived and I had to entertain them",
           "Our plumbing burst and I had to deal with the flooding", "I accidentally left my notebook at a friend's place",
             "I had a sudden allergic reaction and needed medical attention",
         "My computer updated and I lost access to my files", "I underestimated the time needed and couldn't finish on time"
    ]

    cursor.executemany('INSERT INTO work_excuses (excuse) VALUES (?)', [(excuse,) for excuse in work_excuses])

    # Insert 20 excuses into goout_excuses table
    goout_excuses = [
        "I have to babysit my siblings.",
        "I'm waiting for an important delivery.",
        "I need to finish a project for work.",
        "I have a family dinner.",
        "My partner is not feeling well.",
        "I have a headache.",
        "I have a dentist appointment.",
        "I need to take care of my pet.",
        "I have an early meeting tomorrow.",
        "I promised to help a friend move.",
        "I'm feeling under the weather.",
        "I have a lot of chores to catch up on.",
        "I need to visit my grandparents.",
        "I have an online class to attend.",
        "My car is in the shop.",
        "I have to prepare for an interview.",
        "I'm expecting a call from my boss.",
        "I have a personal emergency.",
        "I need to clean the house.",
        "I'm on a strict diet and can't go out."
    ]

    cursor.executemany('INSERT INTO goout_excuses (excuse) VALUES (?)', [(excuse,) for excuse in goout_excuses])

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
