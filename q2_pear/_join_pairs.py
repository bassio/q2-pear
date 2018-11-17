import os
import subprocess
from pathlib import Path
import pandas as pd
import yaml

from q2_types.per_sample_sequences import (SingleLanePerSamplePairedEndFastqDirFmt,
            SingleLanePerSampleSingleEndFastqDirFmt,
            FastqManifestFormat, YamlFormat, FastqGzFormat)


def run_command(cmd, verbose=True):
    print("Running external command line application. This may print "
          "messages to stdout and/or stderr.")
    print("The command being run is below. This command cannot "
          "be manually re-run as it will depend on temporary files that "
          "no longer exist.")
    print("\nCommand:", end=' ')
    print(" ".join(cmd), end='\n\n')
    subprocess.run(cmd, check=True)


def join_pairs(
        demultiplexed_seqs: SingleLanePerSamplePairedEndFastqDirFmt,
        threads: int = 1
        ) -> SingleLanePerSampleSingleEndFastqDirFmt:


    result = SingleLanePerSampleSingleEndFastqDirFmt()

    manifest = pd.read_csv(
        os.path.join(str(demultiplexed_seqs),
                     demultiplexed_seqs.manifest.pathspec),
        header=0, comment='#')
        
    manifest.filename = manifest.filename.apply(
        lambda x: os.path.join(str(demultiplexed_seqs), x))

    phred_offset = yaml.load(open(
        os.path.join(str(demultiplexed_seqs),
                     demultiplexed_seqs.metadata.pathspec)))['phred-offset']

    id_to_fps = manifest.pivot(index='sample-id', columns='direction',
                               values='filename')

    output_manifest = FastqManifestFormat()
    output_manifest_fh = output_manifest.open()
    output_manifest_fh.write('sample-id,filename,direction\n')
    output_manifest_fh.write('# direction is not meaningful in this file '
                             'as these\n')
    output_manifest_fh.write('# data may be derived from forward, reverse, '
                             'or \n')
    output_manifest_fh.write('# joined reads\n')

    for i, (sample_id, (fwd_fp, rev_fp)) in enumerate(id_to_fps.iterrows()):
        # The barcode id, lane number and read number are not relevant
        # here. We might ultimately want to use a dir format other than
        # SingleLanePerSampleSingleEndFastqDirFmt which doesn't care
        # about this information. Similarly, the direction of the read
        # isn't relevant here anymore.
        path = result.sequences.path_maker(sample_id=sample_id,
                                           barcode_id=i,
                                           lane_number=1,
                                           read_number=1)
        
        uncompressed_path = str(path).strip('.gz')
        
        parent_pth = Path(path).parent
        
        sample_id_path = str(parent_pth / sample_id)
        
        assembled_pth = parent_pth / "{}.assembled.fastq".format(sample_id)
        discarded_pth = parent_pth / "{}.discarded.fastq".format(sample_id)
        unassembled_fwd_pth = parent_pth / "{}.unassembled.forward.fastq".format(sample_id)
        unassembled_rev_pth = parent_pth / "{}.unassembled.reverse.fastq".format(sample_id)

        cmd = ['pear',
               '-f', fwd_fp,
               '-r', rev_fp,
               '-o', sample_id_path,
               '--threads', str(threads)
               ]

        run_command(cmd)
        
        
        assembled_pth.rename(Path(uncompressed_path))
        run_command(['gzip', uncompressed_path])
        
        #delete extra files
        extra_files = [discarded_pth, unassembled_fwd_pth, unassembled_rev_pth]
        for f_pth in extra_files:
            try:
                os.remove(str(f_pth))
            except:
                pass
        
        
        output_manifest_fh.write(
            '%s,%s,%s\n' % (sample_id, Path(path).name, 'forward'))

    output_manifest_fh.close()
    result.manifest.write_data(output_manifest, FastqManifestFormat)

    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': phred_offset}))
    result.metadata.write_data(metadata, YamlFormat)

    return result

