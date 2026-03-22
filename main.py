import requests
import json
import sys
from typing import Dict, List, Optional
import time
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


class PincodeLookup:
    def __init__(self):
        self.base_url = "https://api.postalpincode.in/pincode/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def get_pincode_info(self, pincode: str) -> Optional[Dict]:
        try:
            print("🔍 Fetching data...")
            response = self.session.get(
                f"{self.base_url}{pincode}", 
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data or not isinstance(data, list) or len(data) == 0:
                print("❌ No data found for this pincode.")
                return None
                
            return data[0]
            
        except requests.exceptions.Timeout:
            print("⏰ Request timed out. Please check your connection and try again.")
        except requests.exceptions.ConnectionError:
            print("❌ Connection error. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {str(e)}")
        except json.JSONDecodeError:
            print("❌ Invalid response format received.")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {str(e)}")
        
        return None
    
    def display_raw_data(self, data: List[Dict]) -> None:
        
        print("\n📄 Raw JSON Response:")
        print("=" * 50)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    
    def display_formatted_info(self, result: Dict) -> None:
        
        print("\n📋 Formatted Information:")
        print("=" * 60)
        
        message = result.get('Message', 'No message')
        status = result.get('Status', 'Unknown')
        
        print(f"📊 Status: {status}")
        print(f"💬 Message: {message}")
        
        post_offices = result.get('PostOffice', [])
        if post_offices and isinstance(post_offices, list) and len(post_offices) > 0:
            print(f"🏢 Found {len(post_offices)} Post Office(s):")
            print("-" * 60)
            
            for i, office in enumerate(post_offices, 1):
                print(f"\n📍 Location {i}:")
                print(f"   🏢 Name: {office.get('Name', 'N/A')}")
                print(f"   🏷️  Branch Type: {office.get('BranchType', 'N/A')}")
                print(f"   🚚 Delivery Status: {office.get('DeliveryStatus', 'N/A')}")
                print(f"   🌐 Circle: {office.get('Circle', 'N/A')}")
                print(f"   🏘️  District: {office.get('District', 'N/A')}")
                print(f"   🔧 Division: {office.get('Division', 'N/A')}")
                print(f"   🗺️  Region: {office.get('Region', 'N/A')}")
                print(f"   🏳️  State: {office.get('State', 'N/A')}")
                print(f"   🌍 Country: {office.get('Country', 'N/A')}")
                print(f"   📞 Telephone: {office.get('Telephone', 'N/A')}")
                print(f"   📪 Related Suboffice: {office.get('RelatedSuboffice', 'N/A')}")
                print(f"   🏢 Related Headoffice: {office.get('RelatedHeadoffice', 'N/A')}")
        else:
            print("❌ No post office information available for this pincode.")

def validate_pincode(pincode: str) -> bool:

    return pincode.isdigit() and len(pincode) == 6 and pincode != '000000'

def display_welcome():
    print("📍 Pincode Lookup Tool v2.0")
    print("🌟 Made with ❤️  by @Anujedits76")
    print("=" * 50)
    print("🔍 Get detailed information about any Indian pincode")
    print("📈 Real-time data from official postal database")
    print("=" * 50)

def display_help():
    print("\n❓ Help & Instructions:")
    print("=" * 30)
    print("• Enter a valid 6-digit Indian pincode")
    print("• Example: 110001, 400001, 560001")
    print("• Type 'q' or 'quit' to exit")
    print("• Type 'help' to see this help message")
    print("• Type 'history' to see search history")

class PincodeHistory:
    def __init__(self):
        self.history = []
    
    def add_search(self, pincode: str, success: bool):
        self.history.append({
            'pincode': pincode,
            'success': success,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        })

        if len(self.history) > 20:
            self.history.pop(0)
    
    def display_history(self):
        if not self.history:
            print("📝 No search history yet.")
            return
            
        print("\n📝 Search History:")
        print("=" * 40)
        for i, search in enumerate(self.history, 1):
            status = "✅" if search['success'] else "❌"
            print(f"{i:2d}. {status} {search['pincode']} - {search['timestamp']}")

def main():
    lookup = PincodeLookup()
    history = PincodeHistory()
    
    display_welcome()
    
    search_count = 0
    successful_searches = 0
    
    while True:
        try:
            user_input = input("\n👉 Enter 6-digit Pincode (or 'q' to quit, 'help' for help): ").strip()
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                print(f"\n📊 Final Stats:")
                print(f"   Total Searches: {search_count}")
                print(f"   Successful: {successful_searches}")
                print(f"   Success Rate: {successful_searches/search_count*100:.1f}%" if search_count > 0 else "   Success Rate: 0%")
                print("👋 Thank you for using Pincode Lookup Tool!")
                break
            elif user_input.lower() == 'help':
                display_help()
                continue
            elif user_input.lower() == 'history':
                history.display_history()
                continue
            elif user_input.lower() == 'stats':
                print(f"\n📊 Current Stats:")
                print(f"   Searches: {search_count}")
                print(f"   Successful: {successful_searches}")
                print(f"   Success Rate: {successful_searches/search_count*100:.1f}%" if search_count > 0 else "   Success Rate: 0%")
                continue
                
            if validate_pincode(user_input):
                search_count += 1
                result = lookup.get_pincode_info(user_input)
                
                if result:
                    successful_searches += 1
                    lookup.display_formatted_info(result)
                    show_raw = input("\n🔍 Show raw JSON data? (y/n): ").strip().lower()
                    if show_raw in ['y', 'yes']:
                        lookup.display_raw_data([result])
                
                history.add_search(user_input, result is not None)
                print(f"\n✅ Search completed! ({successful_searches}/{search_count} successful)")
            else:
                print("❌ Please enter a valid 6-digit pincode (e.g., 110001)")
                print("💡 Type 'help' for more information")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using Pincode Lookup Tool!")
            print(f"📊 Final Stats - Searches: {search_count}, Successful: {successful_searches}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ An unexpected error occurred: {str(e)}")
            print("🔧 Please try again or contact support.")

if __name__ == "__main__":
    main()
