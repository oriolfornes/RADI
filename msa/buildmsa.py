import os, sys, re
import optparse
import subprocess

#-------------#
# Config      #
#-------------#
# e.g. conda install -c bioconda clustalo
clustalo_path = "/home/ofornes/.anaconda2.7/bin"
# e.g. conda install -c bioconda mmseqs2
mmseqs_path = "/home/ofornes/.anaconda2.7/bin"
# i.e. directory where uniref.sh was exec
uniref_path = "/home/ofornes/scratch/RADI/uniref"

#-------------#
# Parsers     #
#-------------#

def parse_file(file_name):
    """
    This function parses any file and yields lines one by one.
    
    @input:
    file_name {string}
    @return:
    line {string}

    """
 
    if os.path.exists(file_name):
        # Initialize #
        f = None
        # Open file handle #
        try: f = open(file_name, "rt")
        except: raise ValueError("Could not open file %s" % file_name)
        # For each line... #
        for line in f:
            yield line.strip("\n")
        f.close()
    else:
        raise ValueError("File %s does not exist!" % file_name)

def parse_fasta_file(file_name, clean=True):
    """
    This function parses any FASTA file and yields sequences one by one
    in the form header, sequence.

    @input:
    file_name {string}
    clean {boolean} if true, converts \W to X
    @return:
    line {list} header, sequence

    """

    # Initialize #
    header = ""
    sequence = ""
    # For each line... #
    for line in parse_file(file_name):
        if len(line) == 0: continue
        if line.startswith("#"): continue
        if line.startswith(">"):
            if sequence != "":
                if clean:
                    sequence = re.sub("\W|\d", "X", sequence)
                yield header, sequence
            m = re.search("^>(.+)", line)
            header = m.group(1)
            sequence = ""
        else:
            sequence += line.upper()
    if clean:
        sequence = re.sub("\W|\d", "X", sequence)

    yield header, sequence

#-------------#
# Write       #
#-------------#

def write(file_name=None, content=""):
    """
    This function writes any {content} to a file or to stdout if no
    file is provided. If the file already exists, it pushed the {content}
    at the bottom of the file.

    @input:
    file_name {string}
    content {string}

    """
    if file_name is not None:
        try:
            f = open(file_name, "a")
            f.write("%s\n" % content)
        except:
            raise ValueError("Could create file %s" % file_name)
    else:
        sys.stdout.write("%s\n" % content)

#-------------#
# Functions   #
#-------------#

def parse_options():
    """
    This function parses the command line arguments and returns an optparse
    object.

    """

    parser = optparse.OptionParser("python2.7 %prog -i <input_file> [--dummy=dummy_dir -n <nr_database> -r <redundant_db> -o <output_dir> -s <max_sequences> -v]")

    parser.add_option("--dummy", default="/tmp/", action="store", type="string", dest="dummy_dir", help="Dummy directory (default = /tmp/)", metavar="<dummy_dir>")
    parser.add_option("-i", action="store", type="string", dest="input_file", help="Input file (in FASTA format)", metavar="<input_file>")
    parser.add_option("-n", action="store", default="uniref50", type="string", dest="nr_db", help="Non-redundant database (\"uniref50\", \"uniref90\" or \"uniref100\"; default=uniref50)", metavar="<nr_db>")
    parser.add_option("-o", action="store", default="./", type="string", dest="output_dir", help="Output directory (default = ./)", metavar="<output_dir>")
    parser.add_option("-r", action="store", default="uniref100", type="string", dest="redundant_db", help="Redundant database (\"uniref50\", \"uniref90\" or \"uniref100\"; default=uniref100)", metavar="<redundant_db>")
    parser.add_option("-s", action="store", default=10000, type="int", dest="max_sequences", help="Max. number of sequences (default=10000)", metavar="<max_sequences>")
    parser.add_option("-v", "--verbose", default=False, action="store_true", dest="verbose", help="Verbose mode (default = False)")

    (options, args) = parser.parse_args()

    if options.input_file is None:
        parser.error("missing arguments: type option \"-h\" for help")

    return options

#-------------#
# Main        #
#-------------#

if __name__ == "__main__":

    # Arguments & Options #
    options = parse_options()

    # Initialize #
    msa = []
    sequences = {}
    nr_db = os.path.join(uniref_path, "%s.db" % options.nr_db)
    redundant_db = os.path.join(uniref_path, "%s.db" % options.redundant_db)
    dummy_dir = os.path.abspath(options.dummy_dir)
    
    # Create output dir #
    if not os.path.exists(os.path.abspath(options.output_dir)):
            os.makedirs(os.path.abspath(options.output_dir))

    # Create dummy dir #
    if not os.path.exists(dummy_dir):
            os.makedirs(dummy_dir)

    # Skip if redundant query db already exists #
    redundant_query_db = os.path.join(os.path.abspath(options.output_dir), "query.%s.db" % options.redundant_db)
    if not os.path.exists(redundant_query_db):
        # Skip if nr query db already exists #
        nr_query_db = os.path.join(os.path.abspath(options.output_dir), "query.%s.db" % options.nr_db)
        if not os.path.exists(nr_query_db):
            # Create DB #
            process = subprocess.check_output([os.path.join(mmseqs_path, "mmseqs"), "createdb", os.path.abspath(options.input_file), nr_query_db])
        # Skip if alignment file already exists #
        alignment_file = os.path.join(os.path.abspath(options.output_dir), "query.%s.ali" % options.nr_db)
        if not os.path.exists(alignment_file):
            # Search DB #
            process = subprocess.check_output([os.path.join(mmseqs_path, "mmseqs"), "search", nr_query_db, nr_db, alignment_file, dummy_dir, "--split-memory-limit", "250000000000", "--threads", "32", "--num-iterations", "4"])
        # Create DB #
        process = subprocess.check_output([os.path.join(mmseqs_path, "mmseqs"), "result2profile", nr_query_db, nr_db, alignment_file, redundant_query_db])

    # Skip if alignment file already exists #
    alignment_file = os.path.join(os.path.abspath(options.output_dir), "query.%s.ali" % options.redundant_db)
    if not os.path.exists(alignment_file):
        # Search DB #
        process = subprocess.check_output([os.path.join(mmseqs_path, "mmseqs"), "search", redundant_query_db, redundant_db, alignment_file, dummy_dir, "--max-seqs", "1000000", "--split-memory-limit", "250000000000", "--threads", "32", "-s", "7.5", "--max-seq-id", "0.999"])

    # Skip if sequences file already exists #
    sequences_file = os.path.join(os.path.abspath(options.output_dir), "query.%s.fa" % options.redundant_db)
    if not os.path.exists(sequences_file):
        # Get FASTA sequences #
        process = subprocess.check_output([os.path.join(mmseqs_path, "mmseqs"), "createseqfiledb", redundant_db, alignment_file, sequences_file])

    # Skip if clustalo input file already exists #
    clustalo_in_file = os.path.join(os.path.abspath(options.output_dir), "clustalo.in.fa")
    if not os.path.exists(clustalo_in_file):
        # For header, sequence... #
        for header, sequence in parse_fasta_file(os.path.abspath(options.input_file)):
            # Add to MSA #
            msa.append((header, sequence))
            sequences.setdefault(sequence, header)
            break
        # For header, sequence... #
        for header, sequence in parse_fasta_file(sequences_file):
            # Skip if sequence already exists #
            if sequence in sequences: continue
            # Add to MSA #
            msa.append((header, sequence))
            sequences.setdefault(sequence, header)
            # End if enough sequences #
            if len(msa) > options.max_sequences: break
        # For header, sequence... #
        for header, sequence in msa:
            # Write #
            write(clustalo_in_file, ">%s\n%s" % (header, sequence))

    # Skip if clustalo input file already exists #
    clustalo_out_file = os.path.join(os.path.abspath(options.output_dir), "clustalo.out.fa")
    if not os.path.exists(clustalo_out_file):
        # Create MSA #
        process = subprocess.check_output([os.path.join(clustalo_path, "clustalo"), "-i", clustalo_in_file, "-o", clustalo_out_file, "--threads=32"])
    
    # Skip if clean MSA already exists #
    msa_file = os.path.join(os.path.abspath(options.output_dir), "msa.fa")
    if not os.path.exists(msa_file):
        # Initialize #
        headers = []
        sequences = []
        # For header, sequence... #
        for header, sequence in parse_fasta_file(clustalo_out_file, clean=False):
            # Add to lists #
            headers.append(header)
            sequences.append(list(sequence))
        # Transpose sequences #
        sequences = zip(*sequences)
        # For each position... #
        for i in reversed(range(len(sequences))):
            # If query position is a gap... #
            if sequences[i][0] == "-": sequences.pop(i)
        # Transpose sequences #
        sequences = zip(*sequences)
        # For each sequence... #
        for i in range(len(headers)):
            # Write #
            write(msa_file, ">%s\n%s" % (headers[i], "".join(sequences[i])))
