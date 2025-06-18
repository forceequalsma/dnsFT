#########################################################################
### DNS Query Test for Windows Client                                 ###
### Gavin Sung, Edimax PA/SQA, 2025-06-04                             ###
#########################################################################

import csv
import time
import dns.resolver
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

CSV_FILE = 'domain5000.csv'
DNS_SERVER = '8.8.8.8'
BATCH_SIZE = 200
BATCH_SLEEP = 1
FULL_LOOP_SLEEP = 1
MAX_WORKERS = 20

resolver = dns.resolver.Resolver()
resolver.nameservers = [DNS_SERVER]

def load_domains(filename):
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        domains = [row[0].strip() for row in reader if row and row[0]]
    return domains

def query_record(domain, record_type):
    try:
        start = time.time()
        answers = resolver.resolve(domain, record_type)
        latency = (time.time() - start) * 1000
        results = [str(rdata) for rdata in answers]
        return f"{domain:<30} [{record_type}] {results[0]:<40} {latency:.2f} ms"
    except Exception as e:
        return f"{domain:<30} [{record_type}] error: {str(e)}"

def main_loop(domains):
    domain_count = len(domains)
    print(f"載入 {domain_count} 個 domain，開始查詢...")

    while True:
        for i in range(0, domain_count, BATCH_SIZE):
            batch = domains[i:i + BATCH_SIZE]
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = []
                for domain in batch:
                    for record_type in ['A', 'AAAA', 'MX']:
                        futures.append(executor.submit(query_record, domain, record_type))
                for future in as_completed(futures):
                    print(future.result())
            print(f"--- 查詢完第 {(i // BATCH_SIZE) + 1} 批，共 {len(batch)} 筆 ---")
            time.sleep(BATCH_SLEEP)
        print("=== 完成一輪查詢，準備重新開始 ===")
        time.sleep(FULL_LOOP_SLEEP)

if __name__ == '__main__':
    if not os.path.exists(CSV_FILE):
        print(f"檔案 {CSV_FILE} 不存在！")
        exit(1)
    domain_list = load_domains(CSV_FILE)
    main_loop(domain_list)
