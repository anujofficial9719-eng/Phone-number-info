📍 Pincode Lookup Tool v2.0
A powerful and user-friendly Python CLI tool to fetch real-time Indian pincode details using the official postal API.
🌟 Features
🔍 Lookup any 6-digit Indian Pincode
📡 Real-time data from Postal API
📋 Clean formatted output
📄 Option to view raw JSON response
📝 Search history tracking (last 20 searches)
📊 Live statistics (success rate, total searches)
⚠️ Error handling (timeout, connection, invalid input)
💡 Help & command support
🚀 Demo

👉 Enter 6-digit Pincode: 110001

📊 Status: Success
💬 Message: Number of Post office(s) found: 1

📍 Location 1:
   🏢 Name: New Delhi G.P.O.
   🏷️  Branch Type: Head Post Office
   🚚 Delivery Status: Delivery
   🏘️  District: New Delhi
   🏳️  State: Delhi
   🌍 Country: India
🛠️ Installation
1. Clone the Repository
Bash
git clone https://github.com/anujofficial9719-eng/Phone-number-info.git
cd Phone-number-info
2. Install Dependencies
Bash
pip install requests
▶️ Usage
Run the script:
Bash
python main.py
⌨️ Commands
Command
Description
pincode
Search pincode
help
Show instructions
history
Show search history
stats
Show statistics
q / quit
Exit program
📌 Input Rules
Must be 6-digit number
Example: 110001, 400001, 560001
Invalid example: 123, abc123, 000000
🧠 How It Works
Uses API:

https://api.postalpincode.in/pincode/{pincode}
Sends request via requests.Session
Parses JSON response
Displays:
Post office details
Location info
Delivery status
📊 Features Breakdown
🔍 Lookup System
Validates input
Fetches API response
Handles errors gracefully
📝 History System
Stores last 20 searches
Tracks:
Pincode
Success/Failure
Timestamp
📈 Stats System
Total searches
Successful searches
Success rate %
⚠️ Error Handling
Handles:
❌ Invalid pincode
⏰ Timeout errors
🌐 Connection issues
📄 Invalid API response
❤️ Credits
Made with ❤️ by @Anujedits76
📜 License
This project is open-source and available under the MIT License.
