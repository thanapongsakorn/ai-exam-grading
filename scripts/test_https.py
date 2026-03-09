import http.client
import ssl
import certifi

def test_https():
    print("Testing HTTPS connection to google.com...")
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        conn = http.client.HTTPSConnection("google.com", context=context)
        conn.request("GET", "/")
        res = conn.getresponse()
        print(f"✅ Success: google.com returned {res.status}")
    except Exception as e:
        print(f"❌ Failed to connect to google.com: {e}")

if __name__ == "__main__":
    test_https()
