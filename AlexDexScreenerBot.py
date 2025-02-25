import requests
import sqlite3
import time
from datetime import datetime
import json
import os
from typing import Dict, List, Optional
import configparser
import telegram # Requires 'python-telegram-bot' package

class DexScreenerBot:
    def __init__(self, config_file: str = "config.ini"):
        self.get_recent_tokens_url = "https://api.dexscreener.com/latest/dex"
        self.rugcheck_url = "https://api.rugcheck.xyz/v1/tokens"
        self.pocket_universe_url = "https://api.pocketuniverse.app"
        self.db_path = "dexscreener_data.db"
        
        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.load_config()
        
        # Telegram bot setup for ToxiSol
        self.telegram_bot = telegram.Bot(token=self.toxi_telegram_token)
        self.chat_id = self.toxi_chat_id
        
        self.setup_database()

    def load_config(self) -> None:
        """Load configuration from config file"""
        self.min_liquidity_threshold = float(self.config['FILTERS']['min_liquidity_threshold'])
        self.pump_threshold = float(self.config['FILTERS']['pump_threshold'])
        self.rug_threshold = float(self.config['FILTERS']['rug_threshold'])
        self.min_volume_24h = float(self.config['FILTERS']['min_volume_24h'])
        
        self.blacklisted_coins = set(coin.strip().upper() for coin in self.config['BLACKLISTS']['coins'].split(',') if coin.strip())
        self.blacklisted_devs = set(dev.strip().lower() for dev in self.config['BLACKLISTS']['developers'].split(',') if dev.strip())
        
        self.pocket_api_key = self.config['API']['pocket_universe_key']
        self.rugcheck_api_key = self.config['API'].get('rugcheck_key', '')
        self.toxi_telegram_token = self.config['API']['toxi_telegram_token']
        self.toxi_chat_id = self.config['API']['toxi_chat_id']

    def setup_database(self) -> None:
        """Initialize SQLite database with necessary tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS token_data (
                    pair_address TEXT PRIMARY KEY,
                    chain_id TEXT,
                    base_token TEXT,
                    quote_token TEXT,
                    dev_address TEXT,
                    created_at INTEGER,
                    initial_price REAL,
                    current_price REAL,
                    liquidity_usd REAL,
                    volume_24h REAL,
                    price_change_24h REAL,
                    status TEXT,
                    last_updated INTEGER,
                    has_fake_volume INTEGER DEFAULT 0,
                    is_bundle INTEGER DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair_address TEXT,
                    timestamp INTEGER,
                    price REAL,
                    volume REAL,
                    liquidity REAL,
                    FOREIGN KEY (pair_address) REFERENCES token_data (pair_address)
                )
            ''')
            conn.commit()

    def send_telegram_notification(self, message: str) -> None:
        """Send notification via Telegram using ToxiSol bot"""
        try:
            self.telegram_bot.send_message(chat_id=self.chat_id, text=message)
            print(f"Notification sent: {message}")
        except Exception as e:
            print(f"Error sending Telegram notification: {e}")

    def toxi_trade(self, action: str, pair_address: str, amount: float) -> bool:
        """Execute trade via ToxiSol bot and confirm execution"""
        try:
            # Construct the command for ToxiSol
            command = f"/{action} {pair_address} {amount}"
            self.send_telegram_notification(command)
            
            # Simulate waiting for ToxiSol to process (adjust based on actual bot response time)
            time.sleep(2)
            
            # Check if trade was successful (mock confirmation; replace with actual logic if ToxiSol provides feedback)
            confirmation_message = f"Checking {action} status for {pair_address}..."
            self.send_telegram_notification(confirmation_message)
            
            # Here, you'd ideally poll ToxiSol for confirmation (e.g., via chat updates or API)
            # For now, assume success after delay and notify
            success_notification = f"{action.upper()} executed successfully for {pair_address}: {amount} SOL"
            self.send_telegram_notification(success_notification)
            return True
        except Exception as e:
            error_message = f"Trade failed: {action} {pair_address} - Error: {str(e)}"
            self.send_telegram_notification(error_message)
            print(error_message)
            return False

    def fetch_new_tokens(self) -> List[Dict]:
        try:
            response = requests.get(self.get_recent_tokens_url)

            # Check response status
            if response.status_code == 404:
                print("Error: API endpoint not found. Check DexScreener API documentation for updates.")
                return []
            elif response.status_code != 200:
                print(f"Error fetching new pairs: HTTP {response.status_code} - {response.text}")
                return []
            
            return response.json()

        except requests.RequestException as e:
            print(f"Error fetching new pairs: {e}")
            return []
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return []

    def fetch_token_data(self, token) -> Dict:
        chain_id = token['chainId']
        token_address = token['tokenAddress']


    ##
    ##      UNUSED
    ##
    def fetch_new_pairs(self) -> List[Dict]:
        """Fetch newly created pairs from DexScreener"""
        try:
            # Use the search endpoint with a broad query (e.g., "SOL" for Solana pairs)
            # Adjust the query based on your target blockchain
            ##TODO add search query to config file
            response = requests.get(f"https://api.dexscreener.com//token-profiles/latest/v1", timeout=10)
        
            # Check response status
            if response.status_code == 404:
                print("Error: API endpoint not found. Check DexScreener API documentation for updates.")
                return []
            elif response.status_code != 200:
                print(f"Error fetching new pairs: HTTP {response.status_code} - {response.text}")
                return []
        
            data = response.json()
            pairs = data.get("pairs", [])
        
            # Filter pairs created in the last 24 hours (adjust as needed)
            current_time = int(time.time() * 1000)  # Convert to milliseconds
            time_threshold = current_time - (24 * 60 * 60 * 1000)  # 24 hours ago
        
            new_pairs = [
                pair for pair in pairs
                if pair.get("pairCreatedAt", 0) >= time_threshold
            ]
        
            print(f"Found {len(new_pairs)} new pairs out of {len(pairs)} total pairs.")
            return new_pairs
    
        except requests.RequestException as e:
            print(f"Error fetching new pairs: {e}")
            return []
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return []
        
    ##
    ##Unused
    ##
    def fetch_pair_data(self, chain_id,  pair_address: str) -> Optional[Dict]:
        """Fetch detailed data for a specific pair"""
        try:
            response = requests.get(f"{self.base_url}/pairs/{chain_id}/{pair_address}")
            response.raise_for_status()
            return response.json().get("pair", None)
        except requests.RequestException as e:
            print(f"Error fetching pair data for {pair_address}: {e}")
            return None

    def check_rugcheck(self, pair_address: str) -> tuple[bool, bool]:
        """Check token status on RugCheck.xyz"""
        try:
            headers = {"Authorization": f"Bearer {self.rugcheck_api_key}"} if self.rugcheck_api_key else {}
            response = requests.get(f"{self.rugcheck_url}/{pair_address}/report", headers=headers)
            response.raise_for_status()
            data = response.json()
            is_good = data.get("score", "") 
            is_bundle = data.get("topHolders", {}).get("bundledSupply", False)
            return is_good, is_bundle
        except requests.RequestException as e:
            print(f"Error checking RugCheck for {pair_address}: {e}")
            return False, False

    def check_fake_volume(self, pair_address: str, volume_24h: float) -> bool:
        """Check if pair has fake volume using Pocket Universe API"""
        try:
            headers = {"Authorization": f"Bearer {self.pocket_api_key}"}
            payload = {"pair_address": pair_address, "volume_24h": volume_24h, "chain_id": "solana"}
            response = requests.post(f"{self.pocket_universe_url}/volume/verify", json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get("has_fake_volume", False)
        except requests.RequestException as e:
            print(f"Error checking fake volume: {e}")
            return False

    def meets_filters(self, pair: Dict) -> bool:
        """Check if pair meets minimum filter requirements"""
        liquidity = float(pair["liquidity"]["usd"])
        volume = float(pair["volume"]["h24"])
        return liquidity >= self.min_liquidity_threshold and volume >= self.min_volume_24h

    def is_blacklisted(self, pair: Dict) -> bool:
        """Check if pair contains blacklisted coins, developers, or has issues"""
        base_token = pair["baseToken"]["symbol"].upper()
        quote_token = pair["quoteToken"]["symbol"].upper()
        dev_address = pair.get("info", {}).get("dev", {}).get("address", "").lower()
        pair_address = pair["pairAddress"]
        volume_24h = float(pair["volume"]["h24"])
        
        is_good, is_bundle = self.check_rugcheck(pair_address)
        if not is_good or is_bundle:
            if is_bundle:
                self.blacklisted_coins.add(base_token)
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE token_data SET is_bundle = 1 WHERE pair_address = ?", (pair_address,))
                    conn.commit()
            self.send_telegram_notification(f"Blacklisted: {base_token} - {'Bundle' if is_bundle else 'Not Good'}")
            return True
            
        if self.check_fake_volume(pair_address, volume_24h):
            self.blacklisted_coins.add(base_token)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE token_data SET has_fake_volume = 1 WHERE pair_address = ?", (pair_address,))
                conn.commit()
            self.send_telegram_notification(f"Blacklisted: {base_token} - Fake Volume Detected")
            return True
            
        if base_token in self.blacklisted_coins or quote_token in self.blacklisted_coins or (dev_address and dev_address in self.blacklisted_devs):
            self.send_telegram_notification(f"Blacklisted token detected: {base_token}")
            return True
        return False

    def analyze_pair(self, pair: Dict) -> Optional[Dict]:
        """Analyze pair for rug pulls and pumps"""
        if self.is_blacklisted(pair) or not self.meets_filters(pair):
            return None

        analysis = {
            "pair_address": pair["pairAddress"],
            "chain_id": pair["chainId"],
            "base_token": pair["baseToken"]["symbol"],
            "quote_token": pair["quoteToken"]["symbol"],
            "dev_address": pair.get("info", {}).get("dev", {}).get("address", ""),
            "price_usd": float(pair["priceUsd"]),
            "liquidity_usd": float(pair["liquidity"]["usd"]),
            "volume_24h": float(pair["volume"]["h24"]),
            "price_change_24h": float(pair["priceChange"]["h24"]),
            "created_at": pair.get("pairCreatedAt", int(time.time() * 1000))
        }

        if analysis["price_change_24h"] >= self.pump_threshold:
            analysis["status"] = "PUMP"
        elif analysis["price_change_24h"] <= self.rug_threshold and analysis["liquidity_usd"] < self.min_liquidity_threshold:
            analysis["status"] = "RUG"
        else:
            analysis["status"] = "NORMAL"

        return analysis

    def save_to_database(self, analysis: Dict) -> None:
        """Save analysis results to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_price FROM token_data WHERE pair_address = ?", (analysis["pair_address"],))
            existing = cursor.fetchone()

            if existing:
                cursor.execute('''
                    UPDATE token_data SET 
                        current_price = ?, liquidity_usd = ?, volume_24h = ?, price_change_24h = ?, 
                        status = ?, last_updated = ?
                    WHERE pair_address = ?
                ''', (analysis["price_usd"], analysis["liquidity_usd"], analysis["volume_24h"], 
                      analysis["price_change_24h"], analysis["status"], int(time.time()), analysis["pair_address"]))
            else:
                cursor.execute('''
                    INSERT INTO token_data (
                        pair_address, chain_id, base_token, quote_token, dev_address, created_at, 
                        initial_price, current_price, liquidity_usd, volume_24h, price_change_24h, status, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (analysis["pair_address"], analysis["chain_id"], analysis["base_token"], analysis["quote_token"], 
                      analysis["dev_address"], analysis["created_at"], analysis["price_usd"], analysis["price_usd"], 
                      analysis["liquidity_usd"], analysis["volume_24h"], analysis["price_change_24h"], analysis["status"], 
                      int(time.time())))

            cursor.execute('''
                INSERT INTO price_history (pair_address, timestamp, price, volume, liquidity)
                VALUES (?, ?, ?, ?, ?)
            ''', (analysis["pair_address"], int(time.time()), analysis["price_usd"], analysis["volume_24h"], 
                  analysis["liquidity_usd"]))
            conn.commit()

    def trade_and_notify(self, pair: Dict, amount: float = 0.1) -> None:
        """Trade selected token via ToxiSol and send notifications"""
        analysis = self.analyze_pair(pair)
        if not analysis:
            return

        action = "buy" if analysis["status"] == "PUMP" else "sell" if analysis["status"] == "RUG" else None
        if action and self.toxi_trade(action, analysis["pair_address"], amount):
            self.save_to_database(analysis)
            notification = f"{action.upper()} {analysis['base_token']}/{analysis['quote_token']} - Status: {analysis['status']}"
            self.send_telegram_notification(notification)

    def detect_patterns(self) -> None:
        """Detect patterns in stored data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT base_token, COUNT(*) as rug_count
                FROM token_data WHERE status = 'RUG' GROUP BY base_token HAVING rug_count > 1
            ''')
            rugs = cursor.fetchall()
            if rugs:
                print("Potential rug pull patterns detected:")
                for token, count in rugs:
                    print(f"Token {token} appeared in {count} rug pulls")
                    self.send_telegram_notification(f"Rug pattern: {token} ({count} occurrences)")

            cursor.execute('''
                SELECT base_token, AVG(price_change_24h) as avg_pump
                FROM token_data WHERE status = 'PUMP' GROUP BY base_token HAVING avg_pump > ?
            ''', (self.pump_threshold,))
            pumps = cursor.fetchall()
            if pumps:
                print("Potential pump patterns detected:")
                for token, avg in pumps:
                    print(f"Token {token} has average pump of {avg:.2f}%")
                    self.send_telegram_notification(f"Pump pattern: {token} (Avg {avg:.2f}%)")

    def run(self, interval: int = 3600) -> None:
        """Main bot loop"""
        while True:
            print(f"Starting analysis at {datetime.now()}")
            new_tokens = self.fetch_new_tokens()
            for token in new_tokens[:50]:
                self.trade_and_notify(token)

            self.detect_patterns()
            print(f"Sleeping for {interval} seconds...")
            time.sleep(interval)

if __name__ == "__main__":
    bot = DexScreenerBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("Bot stopped by user")