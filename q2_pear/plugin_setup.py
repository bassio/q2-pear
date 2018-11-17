
import qiime2.plugin
from q2_types.feature_data import FeatureData, Sequence
from q2_types.feature_table import FeatureTable, Frequency
from q2_types.sample_data import SampleData
from q2_types.per_sample_sequences import (
    Sequences, SequencesWithQuality, PairedEndSequencesWithQuality,
    JoinedSequencesWithQuality)

citations = qiime2.plugin.Citations.load('citations.bib', package='q2_pear')


import q2_pear

plugin = qiime2.plugin.Plugin(
    name='pear',
    version=q2_pear.__version__,
    website='https://github.com/bassio/q2-pear',
    package='q2_pear',
    user_support_text=None,
    short_description='Plugin for joining paired end reads using PEAR (Zhang et al.).',
    description=('This plugin joins paired end reads using PEAR.'),
    citations=[citations['Zhang2014']]
)

plugin.methods.register_function(
    function=q2_pear.join_pairs,
    inputs={
        'demultiplexed_seqs': SampleData[PairedEndSequencesWithQuality]
    },
    parameters={
        'threads': qiime2.plugin.Int % qiime2.plugin.Range(1, None),
    },
    outputs=[
        ('joined_sequences', SampleData[JoinedSequencesWithQuality])
    ],
    input_descriptions={
        'demultiplexed_seqs': ('The demultiplexed paired-end sequences to '
                               'be joined.'),
    },
    parameter_descriptions={
        'threads': ('The number of threads (CPUs) to use for this command.'),
    },
    output_descriptions={
        'joined_sequences': ('The joined sequences.'),
    },
    name='Join paired-end reads.',
    description=('Join paired-end sequence reads using PEAR (Zhang et al.).')
)
