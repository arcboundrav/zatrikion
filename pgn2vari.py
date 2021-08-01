import chess
import chess.pgn
from util import to_pkl, from_pkl
from collections import OrderedDict

################################################################################
# For handling PGN files
################################################################################
# Open a pgn file; return the opened file and its board
def PGN_IN(filename, pgn_path='./../PGNs/'):
    ''' Returns an opened pgn file, named filename.pgn,
    from the current directory, along with its board, and
    main line.
    '''
    full_filename = pgn_path + filename + '.pgn'
    pgn = open(pgn_path + filename + '.pgn')
    pgn_game = chess.pgn.read_game(pgn)
    pgn_BO = pgn_game.board()
    pgn_mainline = pgn_game.main_line()
    result = {'pgn':pgn_game, 'board':pgn_BO, 'main':pgn_mainline}
    return result

# Save a variation as a pickle to the correct subdirectory
def save_vari(vari_to_save, fn, fp='./pkl/training/'):
    to_pkl(vari_to_save, fn, fp)

# Convert a PGN mainline into a list of algebraic notation suitable for
# variation creation
def pgn_to_vari(variname, pklname, pgnname, pgn_path='./../PGNs/'):
    # Load the PGN
    PGN = PGN_IN(pgnname, pgn_path)
    # Convert the mainline into a list of algebraic notation suitable
    # for variation creation
    vari_ML = []
    BO = PGN['board']
    ML = list(PGN['main'])
    for m in ML:
        vari_ML.append(BO.san(m))
        BO.push(m)
    vari_to_save = {}
    vari_to_save['name'] = variname
    vari_to_save['ML'] = vari_ML
    save_vari(vari_to_save, pklname)
    print("Saved: {} as {}".format(variname, pklname))
    print("ML: {}".format(vari_ML))
