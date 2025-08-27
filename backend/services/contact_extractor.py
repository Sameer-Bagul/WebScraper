import re
import logging

logger = logging.getLogger(__name__)

class ContactExtractor:
    def __init__(self):
        # Regex patterns for contact extraction
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self.website_pattern = re.compile(r'https?://(?:[-\w.])+(?::[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?')
    
    def extract_contacts(self, text):
        """Extract contact information from text"""
        if not text:
            return {}
        
        contacts = {}
        
        # Extract emails
        emails = self.email_pattern.findall(text)
        if emails:
            contacts['emails'] = list(set(emails))
        
        # Extract phone numbers
        phones = self.phone_pattern.findall(text)
        if phones:
            formatted_phones = []
            for phone in phones:
                # Format phone number
                formatted = f"({phone[1]}) {phone[2]}-{phone[3]}"
                if phone[0]:
                    formatted = phone[0] + formatted
                formatted_phones.append(formatted)
            contacts['phones'] = list(set(formatted_phones))
        
        # Extract websites
        websites = self.website_pattern.findall(text)
        if websites:
            contacts['websites'] = list(set(websites))
        
        return contacts
    
    def extract_from_page(self, html_content):
        """Extract contacts from HTML page"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Get text content
            text = soup.get_text()
            
            # Extract basic contacts
            contacts = self.extract_contacts(text)
            
            # Look for specific contact elements
            contact_elements = soup.find_all(['a', 'div', 'span'], 
                                           attrs={'class': re.compile(r'contact|email|phone', re.I)})
            
            for element in contact_elements:
                element_text = element.get_text()
                element_contacts = self.extract_contacts(element_text)
                
                # Merge contacts
                for key, values in element_contacts.items():
                    if key in contacts:
                        contacts[key].extend(values)
                        contacts[key] = list(set(contacts[key]))
                    else:
                        contacts[key] = values
            
            return contacts
            
        except Exception as e:
            logger.error(f"Error extracting contacts from page: {e}")
            return {}