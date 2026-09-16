from tqdm import tqdm
import sqlite3
import zstandard as zstd
import adbase as ad
import json

class LLamaExtApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        
        self.adbase.log("\n\n************\n*\n* Welcome to Llama Extractor App   ************\n*\n************\n") #Launch message
        
        self.adbase.log("hello")
        self.run_extract()
        
    def run_extract(self):
        try:
            self.adbase.log("Starting memory-safe extraction")
            self.compress_data()
            self.adbase.log("Compression completed")
        except Exception as e:
            self.adbase.log(f"Extraction failed: {e}")
            
    def compress_data(self):
        """Main export function with proper JSONL handling"""
        try:
            # Initialize compression
            cctx = zstd.ZstdCompressor(level=3)
            chunk_size = 50000
    #        self.adbase.log("hello:36") ######<------------
            # Connect to DB
            conn = sqlite3.connect('/homeassistant/home-assistant_v2.db')
            cursor = conn.cursor()
    #        self.adbase.log("hello:40") ######<------------
            # Stream data directly
            cursor.execute("""
                SELECT
                  sm.entity_id,
                  DATETIME(s.last_updated_ts, 'unixepoch') AS timestamp,
                  s.state,
                  sa.shared_attrs,
                  HEX(s.context_id_bin) AS context_id
                FROM states s
                JOIN states_meta sm ON s.metadata_id = sm.metadata_id
                LEFT JOIN state_attributes sa ON s.attributes_id = sa.attributes_id
                WHERE sm.entity_id IN (
                  SELECT entity_id FROM states_meta
                  WHERE entity_id LIKE 'binary_sensor.%'
                     OR entity_id LIKE 'sensor.%_temperature'
                     OR entity_id LIKE 'light.%'
                )
                ORDER BY s.last_updated_ts
            """)
    #        self.adbase.log("hello:60") ######<------------
            with open('/homeassistant/llama/ha_export.jsonl', 'wb') as f:
                while True:
                    chunk = cursor.fetchmany(chunk_size)
                    if not chunk:
                        break
        #            self.adbase.log("hello:66") ######<------------
                    ## Convert to JSON lines with proper data types
                    
                    for row in chunk:
                        record = {
                            "entity": row[0],
                            "timestamp": row[1],
                            "state": row[2],
                            "attributes": json.loads(row[3]) if row[3] else {},
                            "context": row[4]
                        }
        #                self.adbase.log("hello:77") ######<------------
                        f.write((json.dumps(record) + "\n").encode('utf-8'))
        #    self.adbase.log("hello:78") ######<------------     
            # Compress with Zstandard
        #    self.adbase.log("hello:80")
            with open('/homeassistant/llama/ha_export.jsonl', "rb") as f_in:
                with open('/homeassistant/llama/ha_export.zst', "wb") as f_out:
                    cctx.copy_stream(f_in, f_out)

            # Cleanup and logging
        #    temp_file.unlink()
            self.adbase.log(f"Successfully exported final_file")
            
        except Exception as e:
            self.adbase.log(f"Export failed: {str(e)}")
            #logging.exception("Data export error")
        finally:
            cursor.close()
            conn.close()

    def quick_check(self, kwargs):
        """Validate recent export"""
        export_file = Path("/homeassistant/llama/ha_export.zst")
        if not export_file.exists():
            return

        # Verify first 100 lines
        dctx = zstd.ZstdDecompressor()
        with open("/homeassistant/llama/ha_export.zst", "rb") as f:
            with dctx.stream_reader(f) as reader:
                text_reader = io.TextIOWrapper(reader, encoding="utf-8")
                valid_lines = 0
                for _ in range(100):
                    line = text_reader.readline()
                    if not line:
                        break
                    try:
                        json.loads(line)
                        valid_lines += 1
                    except json.JSONDecodeError:
                        pass

                self.log(f"Data quality check: {valid_lines}/100 valid JSON lines")
            