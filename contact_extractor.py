import re
import logging
from typing import List, Dict, Set
import spacy
from lxml import html

logger = logging.getLogger(__name__)

class ContactExtractor:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/([a-zA-Z0-9-]+)')
        self.twitter_pattern = re.compile(r'twitter\.com/([a-zA-Z0-9_]+)')
        
        # Try to load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_emails(self, text: str) -> Set[str]:
        """Extract email addresses from text"""
        emails = set()
        matches = self.email_pattern.findall(text)
        for match in matches:
            email = match.lower().strip()
            # Filter out common false positives
            if not any(exclude in email for exclude in ['@example.', '@test.', '@placeholder.']):
                emails.add(email)
        return emails
    
    def extract_phones(self, text: str) -> Set[str]:
        """Extract phone numbers from text"""
        phones = set()
        matches = self.phone_pattern.findall(text)
        for match in matches:
            phone = re.sub(r'[^\d+]', '', match)
            if len(phone) >= 10:  # Minimum valid phone length
                phones.add(match.strip())
        return phones
    
    def extract_social_links(self, text: str) -> Dict[str, Set[str]]:
        """Extract social media links"""
        social_links = {
            'linkedin': set(),
            'twitter': set()
        }
        
        # LinkedIn profiles
        linkedin_matches = self.linkedin_pattern.findall(text)
        for match in linkedin_matches:
            social_links['linkedin'].add(f"linkedin.com/in/{match}")
        
        # Twitter profiles
        twitter_matches = self.twitter_pattern.findall(text)
        for match in twitter_matches:
            social_links['twitter'].add(f"twitter.com/{match}")
        
        return social_links
    
    def extract_names_with_spacy(self, text: str) -> Set[str]:
        """Extract person names using spaCy NER"""
        if not self.nlp:
            return set()
        
        names = set()
        try:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()
                    # Filter out single words and common false positives
                    if len(name.split()) >= 2 and len(name) > 3:
                        names.add(name)
        except Exception as e:
            logger.error(f"Error in name extraction: {e}")
        
        return names
    
    def extract_companies_with_spacy(self, text: str) -> Set[str]:
        """Extract company/organization names using spaCy NER"""
        if not self.nlp:
            return set()
        
        companies = set()
        try:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["ORG", "GPE"]:  # Organizations and geopolitical entities
                    company = ent.text.strip()
                    if len(company) > 2:
                        companies.add(company)
        except Exception as e:
            logger.error(f"Error in company extraction: {e}")
        
        return companies
    
    def extract_from_html(self, html_content: str) -> Dict:
        """Extract contacts from HTML content"""
        try:
            # Parse HTML
            tree = html.fromstring(html_content)
            text_content = tree.text_content()
            
            # Extract all contact information
            contacts = {
                'emails': list(self.extract_emails(text_content)),
                'phones': list(self.extract_phones(text_content)),
                'social_links': {k: list(v) for k, v in self.extract_social_links(text_content).items()},
                'names': list(self.extract_names_with_spacy(text_content)),
                'companies': list(self.extract_companies_with_spacy(text_content))
            }
            
            # Extract specific contact sections
            contact_selectors = [
                '.contact', '.contact-info', '.contact-us',
                '.team', '.about-us', '.staff',
                'footer', '.footer'
            ]
            
            for selector in contact_selectors:
                elements = tree.cssselect(selector)
                for element in elements:
                    section_text = element.text_content()
                    
                    # Extract from contact sections
                    section_emails = self.extract_emails(section_text)
                    section_phones = self.extract_phones(section_text)
                    
                    contacts['emails'].extend(list(section_emails))
                    contacts['phones'].extend(list(section_phones))
            
            # Remove duplicates
            contacts['emails'] = list(set(contacts['emails']))
            contacts['phones'] = list(set(contacts['phones']))
            
            return contacts
            
        except Exception as e:
            logger.error(f"Error extracting contacts from HTML: {e}")
            return {
                'emails': [],
                'phones': [],
                'social_links': {'linkedin': [], 'twitter': []},
                'names': [],
                'companies': []
            }
    
    def extract_job_details(self, html_content: str) -> Dict:
        """Extract job-specific information"""
        try:
            tree = html.fromstring(html_content)
            text_content = tree.text_content()
            
            # Job-specific patterns
            salary_pattern = re.compile(r'\$[\d,]+(?:\.\d{2})?(?:\s*-\s*\$[\d,]+(?:\.\d{2})?)?(?:\s*(?:per|\/)\s*(?:hour|year|month))?', re.IGNORECASE)
            location_pattern = re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}\b')
            
            job_details = {
                'salary_ranges': list(set(salary_pattern.findall(text_content))),
                'locations': list(set(location_pattern.findall(text_content))),
                'companies': list(self.extract_companies_with_spacy(text_content)),
                'contacts': self.extract_from_html(html_content)
            }
            
            return job_details
            
        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return {
                'salary_ranges': [],
                'locations': [],
                'companies': [],
                'contacts': {'emails': [], 'phones': [], 'social_links': {'linkedin': [], 'twitter': []}, 'names': [], 'companies': []}
            }
    
    def score_lead_quality(self, contact_data: Dict) -> int:
        """Score lead quality based on available contact information"""
        score = 0
        
        # Email availability (high value)
        if contact_data.get('emails'):
            score += 30
        
        # Phone availability (medium value)
        if contact_data.get('phones'):
            score += 20
        
        # Social links (medium value)
        social_links = contact_data.get('social_links', {})
        if social_links.get('linkedin'):
            score += 15
        if social_links.get('twitter'):
            score += 10
        
        # Names and companies (low-medium value)
        if contact_data.get('names'):
            score += 10
        if contact_data.get('companies'):
            score += 10
        
        # Multiple contact methods bonus
        contact_methods = sum([
            bool(contact_data.get('emails')),
            bool(contact_data.get('phones')),
            bool(social_links.get('linkedin')),
            bool(social_links.get('twitter'))
        ])
        
        if contact_methods >= 2:
            score += 15
        
        return min(score, 100)  # Cap at 100
