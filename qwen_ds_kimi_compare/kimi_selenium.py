from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import time
import platform

class KimiChatClient:
    def __init__(self):
        # Initialize Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Setup browser options after experimental options
        self._setup_browser_options()
        self._setup_browser_fingerprint()
        
        # Initialize Chrome WebDriver with updated capabilities
        service = Service(ChromeDriverManager().install())
        
        # Set required capabilities
        self.chrome_options.set_capability("browserName", "chrome")
        self.chrome_options.set_capability("platformName", "mac")
        
        # Initialize Chrome WebDriver with chrome_options
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        self.driver.implicitly_wait(10)  # Add implicit wait
        self.wait = WebDriverWait(self.driver, 60)
        self._setup_browser_environment()
        
        # Keep track of browser state
        self.is_browser_active = True

    def _setup_browser_options(self):
        # Basic browser configuration
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument('--disable-blink-features')
        self.chrome_options.add_argument('--disable-infobars')
        
        # Enhanced TLS fingerprint
        self.chrome_options.add_argument('--cipher-suite-blacklist=0x0088,0x0087,0x0039,0x0038,0x0044,0x0045,0x0066,0x0032,0x0033,0x0016,0x0013')
        self.chrome_options.add_argument('--use-fake-ui-for-media-stream')
        self.chrome_options.add_argument('--disable-notifications')
        
        # Session persistence
        self.chrome_options.add_argument('--user-data-dir=./chrome_profile')
        self.chrome_options.add_argument('--profile-directory=Default')
        
        # Add random viewport size
        viewport_width = random.randint(1024, 1920)
        viewport_height = random.randint(768, 1080)
        self.chrome_options.add_argument(f'--window-size={viewport_width},{viewport_height}')
        
        # Enhanced user agent with consistent platform info
        os_version = '10_15_7' if platform.system() == 'Darwin' else '10'
        chrome_version = random.randint(90, 120)
        self.chrome_options.add_argument(
            f'--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X {os_version}) '
            f'AppleWebKit/537.36 (KHTML, like Gecko) '
            f'Chrome/{chrome_version}.0.0.0 Safari/537.36'
        )
        
        # Additional privacy and fingerprint protection
        self.chrome_options.add_argument('--disable-webgl')
        self.chrome_options.add_argument('--disable-reading-from-canvas')
        
        # Experimental options
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
    def _setup_browser_fingerprint(self):
        # Additional fingerprint modifications
        self.chrome_options.add_argument('--disable-web-security')
        self.chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        
        # Add random color depth
        color_depth = random.choice([16, 24, 32])
        self.chrome_options.add_argument(f'--color-profile={color_depth}')

        # Add additional security-related options
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--allow-running-insecure-content')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument('--disable-site-isolation-trials')
        
        # Add privacy-focused options
        self.chrome_options.add_argument('--disable-features=EnableEphemeralFlashPermission')
        self.chrome_options.add_argument('--disable-background-timer-throttling')
        self.chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        self.chrome_options.add_argument('--disable-breakpad')
        self.chrome_options.add_argument('--disable-component-extensions-with-background-pages')

    def _setup_browser_environment(self):
        # Execute CDP commands to modify browser fingerprint
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                // Override navigator properties
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { 
                    get: () => [{
                        0: {type: "application/x-google-chrome-pdf"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    }]
                });
                
                // Add random screen properties
                Object.defineProperty(window.screen, 'width', { get: () => Math.floor(Math.random() * (1920 - 1024) + 1024) });
                Object.defineProperty(window.screen, 'height', { get: () => Math.floor(Math.random() * (1080 - 768) + 768) });
                
                // Randomize hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => Math.floor(Math.random() * 8) + 4 });
                
                // Add random device memory
                Object.defineProperty(navigator, 'deviceMemory', { get: () => Math.floor(Math.random() * 8) + 4 });
                
                // Override platform
                Object.defineProperty(navigator, 'platform', { get: () => "MacIntel" });
                
                // Add WebGL fingerprint randomization
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Open Source Technology Center';
                    }
                    if (parameter === 37446) {
                        return 'Mesa DRI Intel(R) HD Graphics';
                    }
                    return getParameter.apply(this, arguments);
                };
                
                // Add language preferences
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Add touch support simulation
                Object.defineProperty(navigator, 'maxTouchPoints', {
                    get: () => Math.floor(Math.random() * 5)
                });
            '''
        })

    def human_like_typing(self, element, text):
        """Simulate human-like typing with realistic timing variations and occasional mistakes."""
        for char in text:
            # Simulate typing mistakes (5% chance)
            if random.random() < 0.05:
                wrong_char = chr(ord(char) + random.randint(-1, 1))
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.2, 0.4))
            
            # Type the correct character with variable delay
            element.send_keys(char)
            
            # Variable delay between keystrokes (40-150ms)
            time.sleep(random.uniform(0.04, 0.15))
            
            # Occasional longer pauses (10% chance)
            if random.random() < 0.1:
                time.sleep(random.uniform(0.5, 2.0))
    
    def move_to_element(self, element):
        """Simulate human-like mouse movement to an element with natural curves and speed variations."""
        action = ActionChains(self.driver)
        
        # Add multiple random waypoints to create natural curved movement
        waypoints = [(random.randint(-100, 100), random.randint(-100, 100)) for _ in range(3)]
        for x, y in waypoints:
            action.move_by_offset(x, y)
            action.pause(random.uniform(0.1, 0.3))
        
        # Move to the actual element with variable speed
        action.move_to_element(element)
        action.pause(random.uniform(0.2, 0.4))
        
        # Add slight hover movement after reaching the element
        action.move_by_offset(random.randint(-5, 5), random.randint(-5, 5))
        action.perform()
        
        # Add a natural pause after movement
        time.sleep(random.uniform(0.3, 0.7))

    def human_like_typing(self, element, text):
        """Simulate human-like typing with realistic timing variations and occasional mistakes."""
        for char in text:
            # Simulate typing mistakes (5% chance)
            if random.random() < 0.05:
                wrong_char = chr(ord(char) + random.randint(-1, 1))
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.2, 0.4))
            
            # Type the correct character with variable delay
            element.send_keys(char)
            
            # Variable delay between keystrokes (40-150ms)
            time.sleep(random.uniform(0.04, 0.15))
            
            # Occasional longer pauses (10% chance)
            if random.random() < 0.1:
                time.sleep(random.uniform(0.5, 2.0))
    
    def start_chat(self):
        """Navigate to DeepSeek chat and initialize the session."""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.is_browser_active:
                    print("Browser is not active, reinitializing...")
                    self.__init__()
                
                url='https://kimi.moonshot.cn/chat/'
                self.driver.get(url)
                
                # Check if already logged in by looking for login element
                try:
                    login_element = self.driver.find_element(By.CSS_SELECTOR, 'em[data-v-4fda06fd]')
                    if login_element.text == 'Login':
                        print("Not logged in yet. Please log in manually.")
                        # Wait for manual login
                        self.wait.until_not(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'em[data-v-4fda06fd]'))
                        )
                except:
                    print("Already logged in")
                
                # Wait for the chat interface to load with increased timeout
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.attachment-button')))
                    print("Successfully connected to chat interface")
                    return True
                except TimeoutException:
                    print(f"Attempt {retry_count + 1}: Failed to load chat interface, retrying...")
                    retry_count += 1
                    time.sleep(2)
                    continue
                    
            except Exception as e:
                print(f"Attempt {retry_count + 1}: Error during chat initialization: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2)
                    continue
                else:
                    print("Failed to initialize chat after maximum retries")
                    self.close()
                    raise
        
        return False
    
    def store_session(self):
        # Save cookies and session information after successful login
        cookies = self.driver.get_cookies()
        session_data = {
            'cookies': cookies,
            'session_id': self.driver.session_id,
            'window_handles': self.driver.window_handles,
            'current_url': self.driver.current_url
        }
        
        # Save session data to pickle file
        import pickle
        with open('kimi_cookies.pkl', 'wb') as f:
            pickle.dump(session_data, f)
    
    def load_session(self):
        """Load saved session data and restore cookies."""
        try:
            import pickle
            with open('kimi_cookies.pkl', 'rb') as f:
                session_data = pickle.load(f)
            
            # Restore cookies
            for cookie in session_data['cookies']:
                self.driver.add_cookie(cookie)
            
            # Refresh the page to apply cookies
            self.driver.refresh()
            return True
        except Exception as e:
            print(f"Failed to load session: {str(e)}")
            return False
    
    def send_message(self, message):
        """Send a message to the chat interface and wait for response."""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.is_browser_active:
                    print("Browser is not active, reinitializing...")
                    self.start_chat()
                
                # Find the chat input editor div element with all required attributes
                chat_input = self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'chat-input-editor'))
                )
                
                # Clear any existing content
                chat_input.clear()
                # Type the message with human-like behavior
                self.human_like_typing(chat_input, message)
                
                # Find and click the specified button with natural movement
                send_button = self.driver.find_element(By.CLASS_NAME, 'send-button')
                send_button.click()
                
                # Add random delay before waiting for response
                time.sleep(random.uniform(0.5, 1.5))
                
                # Wait for response and find the last segment-content element
                segment_contents = self.wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'segment-content'))
                )
                last_segment = segment_contents[-1] if segment_contents else None
                
                if not last_segment:
                    raise Exception("No response segments found")
                
                # Wait for the response to complete by checking for actions content
                self.wait.until(
                    lambda _: last_segment.find_elements(By.CLASS_NAME, 'segment-assistant-actions-content')
                )
                
                # Extract the response text from paragraphs
                paragraphs = last_segment.find_elements(By.CLASS_NAME, 'paragraph')
                response_text = '\n'.join([p.text for p in paragraphs])
                
                return response_text
                
            except Exception as e:
                print(f"Attempt {retry_count + 1}: Error sending message: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2)
                    try:
                        self.start_chat()
                        continue
                    except:
                        pass
                return None
    
    def close(self):
        """Close the browser and clean up resources."""
        if self.driver:
            self.driver.quit()

# Example usage
def main():
    client = KimiChatClient()
    try:
        # Try to load existing session first
        if client.load_session():
            print("Successfully loaded previous session")
            client.start_chat()
            response = client.send_message("hello")
            print(f"Response: {response}")
        else:
            print("No previous session found or failed to load")
            client.store_session()
        

        # response = client.send_message("Hello, how are you?")
        # print("Response:", response)
    finally:
        client.store_session()
        client.close()

if __name__ == '__main__':
    main()