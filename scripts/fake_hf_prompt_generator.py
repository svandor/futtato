#!/usr/bin/env python
import sys, json, time, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--prompt', type=str, default='')
parser.add_argument('--n', type=int, default=3)
parser.add_argument('--max', type=int, default=128)
# accept unknown args so the worker can pass --model/--device/etc without failing
args, _ = parser.parse_known_args()

def main():
    p = args.prompt or 'teszt prompt'
    # simulate a little processing
    time.sleep(0.5)
    outputs = [f"EZ EGY SZIMULÁLT MAGYAR PROMPT: {p} - VAR{i}" for i in range(1, args.n+1)]
    print(json.dumps(outputs, ensure_ascii=False))

if __name__ == '__main__':
    main()
