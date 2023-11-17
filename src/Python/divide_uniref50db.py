import os
from argparse import ArgumentParser
from multiprocessing import Pool
from pathlib import Path


def get_option():
    argparser = ArgumentParser()
    argparser.add_argument('-i', '--input', type=str, required=True, help="UniRef50 XML file.")
    argparser.add_argument('-n', '--num_block', type=int, default=100, help="Number of files to split. (default: 100)")
    argparser.add_argument('-e', '--exclude', nargs="*", type=str, default=["sequence"], help="Elements name to be excluded. (e.g. -e sequence \"UniParc ID\" length) (default: sequence)")
    argparser.add_argument('-o', '--outdir', type=str, default="./", help="Output directory. (default: current directory)")
    return argparser.parse_args()

def main():
    args = get_option()
    file_ref50xml = Path(args.input)
    sdb = SplitDB(file_ref50xml, args.exclude, args.num_block, args.outdir)
    sdb.run()

class SplitDB:
    def __init__(self, input_file: Path, elements=["sequence"], num_split=100, outdir="./"):
        """Split UniRef50 XML file.
        Args:
            input_file (Path): Input UniRef50 XML file.
            elements (list, optional): Elements name to be excluded. Defaults to ["sequence"].
            num_split (int, optional): Number of files to split. Defaults to 100.
            outdir (str, optional): Output directory. Defaults to "./".
        """
        self.file_ref50xml = input_file
        self.exc_elements = elements
        self.outdir = outdir
        file_size = self.file_ref50xml.stat().st_size
        chunk_size = file_size // num_split
        self.chunks = self.set_chunk(file_size, chunk_size, num_split)
        self.xml_info = self.get_xmlinfo()
        
    def set_chunk(self, file_size: int, chunk_size: int, num_split: int):
        start, end = 0, chunk_size
        chunks = []

        with self.file_ref50xml.open(encoding="utf-8", errors="ignore") as f:
            for num in range(num_split - 1):
                f.seek(end)
                f.readline()
                end = f.tell()
                chunks.append((num + 1, start, end))
                start, end = end, end + chunk_size
            chunks.append((num_split, start, file_size))
        return chunks

    def get_xmlinfo(self):
        with self.file_ref50xml.open() as f:
            xml_info = ""
            for line in f:
                if "<entry" in line:
                    break
                else:
                    xml_info += line
        return xml_info

    def run(self):
        with Pool(processes=os.cpu_count()) as pool:
            pool.starmap(self.split, self.chunks)
        
    def split(self, num: int, start: int, end: int):
        current = start
        output_file = Path(self.outdir + "/cut_res_" + str(num) + ".xml")
        with self.file_ref50xml.open() as f, output_file.open(mode="w") as o:
            f.seek(start)
            if not num == 1:
                o.write(self.xml_info)
                for line in f:
                    current += len(line.encode())
                    if ('<entry' in line):
                        o.write(f"{line}")
                        break
            else:
                o.write(f.readline())
            for line in f:
                current += len(line.encode())
                if (current >= end) and ('<entry' in line):
                    o.write("</UniRef50>\n")
                    break
                if (not line.isspace()) and (all((not s in line) for s in self.exc_elements)):
                    o.write(f"{line}")

if __name__ == '__main__':
    main()