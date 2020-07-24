'''
Takes 3 arguments:
1. The previous genome 
2. The new genome generated from the shim code
3. The path and name of the file to output eg. $IDDATA/shim1.txt
'''

from .genome_tools import ID_BCell

from .logging_utils import logging, getLogger
logger = getLogger(__name__)


def process(options, args):
    logger.debug('Starting')

    # TODO refactor arguments to use options named tuple
    # Check for unstructured arguments for inputs and output files
    if len(args) < 2:
        msg = 'Must provide at least two file paths to genomes to be compared.'
        logger.error(msg)
        raise Exception(msg)

    # Extract unstructured arguments
    g1_path, g2_path = args[:2]
    output_path      = args[2] if (len(args) > 2) else 'compare.txt'

    try:
        logger.info('Loading ID_BCell genome 1 [%s]', g1_path)
        g1 = ID_BCell()
        g1.load(g1_path)

    except Exception as ex:
        logger.error('Failed to load ID_BCell genome 1 [%s]', g1_path, exc_info=ex)
        raise ex

    try:
        logger.info('Loading ID_BCell genome 2 [%s]', g2_path)
        g2 = ID_BCell()
        g2.load(g2_path)

    except Exception as ex:
        logger.error('Failed to load ID_BCell genome 2 [%s]', g2_path, exc_info=ex)
        raise ex

    try:
        logger.info('Writing comparison to [%s]', output_path)

        # TODO convert output to pandas .csv file
        with open(output_path, 'w') as output_file:
            # Write file header
            output_file.write("Type    Shim no.    Original   Orientation    Replacement    Orientation\n")

            # Process each magnet type
            for list_key in g1.genome.magnet_lists.keys():

                # Process each magnet of type
                for i, (g1_mag, g2_mag) in enumerate(zip(g1.genome.magnet_lists[list_key],
                                                         g2.genome.magnet_lists[list_key])):

                    # Only output magnets that do not match between files
                    if g1_mag != g2_mag:
                        row_data = (list_key, i, g1_mag[0], g1_mag[1], g2_mag[0], g2_mag[1])

                        logger.debug('Change found on magnet %d [%s]', i, row_data)
                        output_file.write('%2s \t%3i  \t\t%3s   \t%1i  \t\t%3s  \t\t%1i\n' % row_data)

    except Exception as ex:
        logger.error('Failed to write comparison to [%s]', output_path, exc_info=ex)
        raise ex

    logger.debug('Halting')

if __name__ == '__main__' :
    import optparse
    usage = "%prog [options] OutputFile"
    parser = optparse.OptionParser(usage=usage)

    # TODO refactor arguments to use named values
    (options, args) = parser.parse_args()
    process(options, args)
