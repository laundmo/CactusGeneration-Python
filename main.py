from cactusheight import generate
from stream_processor import stream_processor
import itertools
from tqdm import tqdm

chunk_size = 10

def integers():
    for i in itertools.count(step=chunk_size):
        yield i

def generate_and_check(i):
    results = []
    for seed in range(i, i + chunk_size):
        a = generate(seed)
        if a > 5:
            results.append([a, seed])
    if len(results) > 0:
        return results

if __name__ == "__main__":
    for result in tqdm(stream_processor(integers(), generate_and_check, num_workers=24), unit_scale=chunk_size):
        if result[0]:
            tqdm.write(f"chunk {result[1]} results {result[0]}")