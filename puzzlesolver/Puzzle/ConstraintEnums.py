
from enum import Enum
import inspect
from typing import Iterable, Type


class ToolEnum(Enum):
    pass


class BoolToolEnum(ToolEnum):
    pass


class LocalToolEnum(ToolEnum):
    pass


class SimpleGlobalConstraintsE(BoolToolEnum):
    NORMAL_SUDOKU_RULES_DO_NOT_APPLY = 'Normal Sudoku Rules Do Not Apply'
    UNKNOWN_EMPTY_CELLS = 'Unknown Empty Cells'
    DIGITS_DO_NOT_REPEAT_ON_COLUMNS = 'Digits Do Not Repeat On Columns'
    DIGITS_DO_NOT_REPEAT_ON_ANY_DIAGONALS = 'Digits Do Not Repeat On Any Diagonals'
    ONE_OF_EACH_DIGIT_ON_COLUMNS = 'One Of Each Digit On Columns'

    ANTIKNIGHT = 'Antiknight'
    ANTIKING = 'Antiking'
    DISJOINT_GROUPS = 'Disjoint Groups'
    NONCONSECUTIVE = 'Nonconsecutive'
    NONRATIO = 'Nonratio'
    POSITIVE_DIAGONAL = 'Positive Diagonal'
    NEGATIVE_DIAGONAL = 'Negative Diagonal'
    POSITIVE_ANTIDIAGONAL = 'Positive Antidiagonal'
    NEGATIVE_ANTIDIAGONAL = 'Negative Antidiagonal'
    ODD_EVEN_PARITY_MIRROR_ALONG_POSITIVE_DIAGONAL = 'Odd/Even Parity Mirror Along Positive Diagonal'
    ODD_EVEN_PARITY_MIRROR_ALONG_NEGATIVE_DIAGONAL = 'Odd/Even Parity Mirror Along Negative Diagonal'

    EVENS_MUST_SEE_IDENTICAL_DIGIT_BY_KNIGHTS_MOVE = 'Evens Must See Identical Digit By Knights Move'

    TWO_BY_TWO_BOX_GLOBAL_ENTROPY = 'Two By Two Box Global Entropy'
    GLOBAL_INDEXING_COLUMN = 'Global Indexing Column'
    GLOBAL_INDEXING_ROW = 'Global Indexing Row'
    GLOBAL_INDEXING_REGION = 'Global Indexing Region'
    GLOBAL_INDEXING_DISJOINT_GROUPS = 'Global Indexing Disjoint Groups'
    AT_LEAST_ONE_ACE_RULE = 'At Least One Ace Rule'
    SINGLE_NADIR = 'Single Nadir'
    CONSECUTIVE_ENTANGLEMENT = 'Consecutive Entanglement'
    CONSECUTIVE_CLOSE_NEIGHBORS = 'Consecutive Close Neighbors'
    ORTHOGONALLY_ADJACENT_CELLS_ARE_NOT_DIVISORS = 'Orthogonally Adjacent Cells Are Not Divisors'
    DUTCH_MIRACLE = 'Dutch Miracle'

    ALL_ODD_DIGITS_ARE_ORTHOGONALLY_CONNECTED = 'All Odd Digits Are Orthogonally Connected'
    ODD_DIGITS_CANNOT_GATHER_IN_A_2X2_SQUARE = 'Odd Digits Cannot Gather In A 2x2 Square'
    EXACTLY_TWO_FRIENDLY_CELLS_IN_EVERY_ROW_COL_BOX = 'Exactly Two Friendly Cells In Every Row Col Box'
    EXACTLY_ONE_REGION_IS_A_MAGIC_SQUARE = 'Exactly One Region Is A Magic Square'
    THREE_IN_THE_CORNER = 'Three In The Corner'

    ONE_COLUMN_IS_MAGIC = 'One Column Is Magic'


# Add to existing local constraints
class LocalConstraintsModifiersE(BoolToolEnum):
    # Edge constraints
    ALL_RATIOS_GIVEN = 'All Ratios Given'
    ALL_DIFFERENCES_GIVEN = 'All Differences Given'
    ALL_X_GIVEN = "All X's Given"
    ALL_V_GIVEN = "All V's Given"
    ALL_XV_GIVEN = "All XV's Given"
    ALL_YIN_YANG_KROPKI_GIVEN = "All Yin Yang Kropki Given"
    ALL_XY_DIFFERENCES_GIVEN = 'All XY Differences Given'
    EDGE_SQUARE_NUMBER_ALL_DIFFERENT = 'Edge Square Number All Different'

    # Single Cell Constraints
    ALL_RADARS_GIVEN = 'All Radars Given'
    ALL_INDEXING_COLUMN_GIVEN = 'All Indexing Column Given'
    ALL_INDEXING_COLUMN_IN_USED_COLUMNS_GIVEN = 'All Indexing Column In Used Columns Given'
    ALL_INDEXING_ROW_GIVEN = 'All Indexing Row Given'
    ALL_NURIMISAKI_UNSHADED_ENDPOINTS_GIVEN = 'All Nurimisaki Unshaded Endpoints Given'
    ALL_UNKNOWN_REGIONS_NEIGHBOUR_CELLS_SAME_REGION_COUNT_EXCEPT_ITSELF_GIVEN = 'All Unknown Regions Neighbour Cells Same Region Count Except Itself Given'

    # Corner Constraints
    ALL_BORDER_SQUARE_DIAGONALS_SUM_NOT_EQUAL_GIVEN = 'All Border Square Diagonals Sum Not Equal Given'
    ALL_CORNER_CELLS_BELONG_TO_THE_SAME_REGION_GIVEN = 'All Corner Cells Belong To The Same Region Given'
    ALL_CORNER_CELLS_BELONG_TO_EXACLT_THREE_REGIONS_GIVEN = 'All Corner Cells Belong To Exactly Three Regions Given'

    # Cage Constraints
    ALL_CAGE_TOTALS_ARE_UNIQUE = 'All Cage Totals Are Unique'
    ADJACENT_CAGES_HAVE_CONSECUTIVE_TOTALS = 'Adjacent Cages Have Consecutive Totals'
    ADJACENT_CAGES_HAVE_DIFFERENT_TOTALS = 'Adjacent Cages Have Different Totals'
    ADJACENT_CAGES_ARE_GERMAN_WHISPERS = 'Adjacent Cages Are German Whispers'
    DIVISIBLE_KILLER_CAGE_SUMS_ARE_UNIQUE = 'Divisible Killer Cage Sums Are Unique'
    VAULTED_KILLER_CAGES = 'Vaulted Killer Cages'

    # Line Constraints
    PALINDROMES_ONLY_HAVE_TWO_DIGITS = 'Palindromes Only Have Two Digits'
    DISTINCT_RENBANS = 'Distinct Renbans'
    TWO_DIGIT_NUMBERS_DO_NOT_REPEAT_ON_TWO_DIGIT_THERMOS = 'Two Digit Numbers Do Not Repeat On Two Digit Thermos'
    SUM_LINES_DO_NOT_PASS_THROUGH_EMPTY_CELLS = 'Sum Lines Do Not Pass Through Empty Cells'

    # RC Constraints
    EACH_CELL_BELONGS_TO_A_GALAXY = 'Each Cell Belongs To A Galaxy'
    DIGITS_DO_NOT_REPEAT_WITHIN_A_GALAXY = 'Digits Do Not Repeat Within A Galaxy'
    EVERY_GALAXY_CONTAINS_ONE_STAR = 'Every Galaxy Contains One Star'
    ALL_BALANCED_LOOP_CELL_OR_BORDER_GIVEN = 'All Balanced Loop Cell Or Border Given'


class GlobalRegionConstraintsE(BoolToolEnum):
    UNKNOWN_REGIONS = 'Unknown Regions'
    UNKNOWN_REGIONS_DO_NOT_COVER_2X2_SECTIONS = 'Unknown Regions Do Not Cover 2x2 Sections'
    UNKNOWN_NINE_3X3_REGIONS = 'Unknown Nine 3x3 Regions'
    UNKNOWN_NUMBERED_REGIONS = "Unknown Numbered Regions"

    AMBIGUOUS_ENTROPY = 'Ambiguous Entropy'

    YIN_YANG = 'Yin Yang'
    YIN_YANG_UNKNOWN_REGIONS_FULLY_SHADED_OR_FULLY_UNSHADED = 'Yin Yang Unknown Regions Fully Shaded Or Fully Unshaded'

    NURIMISAKI = 'Nurimisaki'
    CELLS_ALONG_NURIMISAKI_PATH_HAVE_A_DIFFERENCE_OF_AT_LEAST_5 = 'Cells Along Nurimisaki Path Have A Difference Of At Least 5'

    NORINORI = 'Norinori'
    ALL_SHADED_NORINORI_CELLS_ARE_ODD = "All Shaded Norinori Cells Are Odd"
    NORINORI_KILLER_CAGES = "Norinori Killer Cages"

    L_SHAPED_REGIONS = 'L-Shaped Regions'
    CROSSED_PATHS = 'Crossed Paths'
    TWO_CONTIGUOUS_REGIONS = 'Two Contiguous Regions'
    BATTLESTAR = 'Battlestar'

    CENTER_CELLS_LOOP = 'Center Cells Loop'
    CENTER_CELLS_LOOP_PASSES_THROUGH_EVERY_CELL_EXCEPT_DIGIT_1 = 'Center Cells Loop Passes Through Every Cell Except Digit 1'
    LOOP_ENTER_AND_EXITS_EVERY_REGION_EXACTLY_ONCE = 'Loop Enter And Exits Every Region Exactly Once'


class ValueModifierConstraintsE(BoolToolEnum):
    VAMPIRE_AND_PREY = 'Vampire And Prey'
    MARKED_CELLS = 'Marked Cells'
    DOUBLERS = 'Doublers'
    NEGATORS = 'Negators'
    HOT_CELLS = 'Hot Cells'
    COLD_CELLS = 'Cold Cells'
    CELL_CANNOT_BE_BOTH_HOT_AND_COLD = 'Cell Cannot Be Both Hot And Cold'
    DECREMENT_FOUNTAINS = 'Decrement Fountains'
    MULTIPLIERS = 'Multipliers'


class SingleCellConstraintsE(LocalToolEnum):
    ODD = 'Odd'
    EVEN = 'Even'
    MAXIMUM = 'Maximum'
    MINIMUM = 'Minimum'
    ODD_MINESWEEPER = 'Odd Minesweeper'
    EVEN_MINESWEEPER = 'Even Minesweeper'
    WATCHTOWER = 'Watchtower'
    NOT_WATCHTOWER = 'Not Watchtower'
    FARSIGHT = 'Farsight'
    RADAR = 'Radar'
    COUNT_SAME_PARITY_NEIGHBOUR_CELLS = 'Count Same Parity Neighbour Cells'
    ORTHOGONAL_SUM = 'Orthogonal Sum'
    INDEXING_COLUMN = 'Indexing Column'
    INDEXING_ROW = 'Indexing Row'
    LOW_DIGIT = 'Low Digit'
    HIGH_DIGIT = 'High Digit'
    FRIENDLY_CELL = 'Friendly Cell'
    DIAGONALLY_ADJACENT_SUM = 'Diagonally Adjacent Sum'
    PRIME_CELL = 'Prime Cell'
    ADJACENT_CELLS_IN_DIFFERENT_DIRECTIONS_HAVE_OPPOSITE_PARITY = 'Adjacent Cells In Different Directions Have Opposite Parity'
    SNOWBALL = 'Snowball'
    SANDWICH_ROW_COL_COUNT = 'Sandwich Row Column Count'

    YIN_YANG_UNSHADED_CELL = 'Yin Yang Unshaded Cell'
    YIN_YANG_SHADED_CELL = 'Yin Yang Shaded Cell'
    YIN_YANG_MINESWEEPER = 'Yin Yang Minesweeper'
    YIN_YANG_SEEN_UNSHADED_CELLS = 'Yin Yang Seen Unshaded Cells'
    YIN_YANG_SEEN_SHADED_CELLS = 'Yin Yang Seen Shaded Cells'
    YIN_YANG_SAME_COLOR_ADJACENT_COUNT = 'Yin Yang Same Color Adjacent Count'

    NURIMISAKI_UNSHADED_ENDPOINTS = 'Nurimisaki Unshaded Endpoints'

    L_SHAPED_REGION_BEND_COUNT = 'L-Shaped Region Bend Count'
    L_SHAPED_REGION_SUM = 'L-Shaped Region Sum'

    CELL_INSIDE_EDGE_LOOP = 'Cell Inside Edge Loop'
    CELL_OUTSIDE_EDGE_LOOP = 'Cell Outside Edge Loop'
    COUNT_CELL_EDGES_BELONGING_TO_EDGE_LOOP = 'Count Cell Edges Belonging To Edge Loop'
    COUNT_SEEN_CELLS_INSIDE_EDGE_LOOP = 'Count Seen Cells Inside Edge Loop'

    TWO_CONTIGUOUS_REGIONS_ROW_COLUMN_OPPOSITE_SET_COUNT = 'Two Contiguous Regions Row Column Opposite Set Count'
    UNKNOWN_REGIONS_NEIGHBOUR_CELLS_SAME_REGION_COUNT_EXCEPT_ITSELF = 'Unknown Regions Neighbour Cells Same Region Count Except Itself'
    SEEN_REGION_BORDERS_COUNT = 'Seen Region Borders Count'
    COUNT_REGION_SUM_LINE_CELLS_IN_REGION = 'Count Region Sum Line Cells In Region'

    GALAXY_SUM_EXCEPT_STAR = 'Galaxy Sum Except Star'

    REGION_LOOP_SUM_CELL = 'Region Loop Sum Cell'


class SingleCellArrowConstraintsE(LocalToolEnum):
    L_SHAPED_REGION_ARROW_POINTS_TO_BEND = 'L-Shaped Region Arrow Points To Bend'


class SingleCellMultiArrowConstraintsE(LocalToolEnum):
    YIN_YANG_SHADED_CELL_COUNT_IN_DIRECTIONS_EXCEPT_ITSELF = 'Yin Yang Shaded Cell Count In Directions Except Itself'
    NEXT_NUMBERED_REGION_DISTANCE_ARROWS = 'Next Numbered Region Distance Arrows'
    COUNT_CELLS_NOT_IN_THE_SAME_REGION_ARROWS = 'Count Cells Not In The Same Region Arrows'


class EdgeConstraintsE(LocalToolEnum):
    RATIO = 'Ratio'
    DIFFERENCE = 'Difference'
    XV = 'XV'
    X_OR_V = 'X Or V'
    EDGE_INEQUALITY = 'Edge Inequality'
    EDGE_SUM = 'Edge Sum'
    EDGE_PRODUCT = 'Edge Product'
    EDGE_MODULO = 'Edge Modulo'
    EDGE_FACTOR = 'Edge Factor'
    XY_DIFFERENCES = 'XY Differences'
    TWO_DIGIT_MULTIPLES = 'Two Digit Multiples'
    EDGE_SQUARE_NUMBER = 'Edge Square Number'
    EDGE_EXACTLY_ONE_FRIENDLY_CELL = 'Edge Exactly One Friendly Cell'

    YIN_YANG_KROPKI = 'Yin Yang Kropki'
    UNKNOWN_REGION_BORDER = 'Unknown Region Border'

    SAME_AMBIGUOUS_ENTROPY_EDGE = 'Same Ambiguous Entropy Edge'
    DIFFERENT_AMBIGUOUS_ENTROPY_EDGE = 'Different Ambiguous Entropy Edge'


class CornerConstraintsE(LocalToolEnum):
    QUADRUPLE = 'Quadruple'
    CORNER_SUM = 'Corner Sum'
    CORNER_X = 'Corner X'
    CORNER_SUM_OF_THREE_EQUALS_THE_OTHER = 'Corner Sum of Three Equals The Other'
    CORNER_EVEN_COUNT = 'Corner Even Count'
    CORNER_ODD_COUNT = 'Corner Odd Count'

    BORDER_SQUARE_DIAGONALS_SUM_NOT_EQUAL = 'Border Square Diagonals Sum Not Equal'

    CORNER_CELLS_BELONG_TO_EXACTLY_THREE_REGIONS = 'Corner Cells Belong To Exactly Three Regions'
    CORNER_CELLS_BELONG_TO_SAME_REGION = 'Corner Cells Belong To Same Region'

    EDGE_LOOP_PASSES_STRAIGHT_ON_CORNER_AND_TURNS_AFTER_AT_LEAST_ONCE = 'Edge Loop Passes Straight On Corner And Turns After At Least Once'
    EDGE_LOOP_TURNS_ON_CORNER_AND_DOES_NOT_TURN_AFTER = 'Edge Loop Turns On Corner And Does Not Turn After'


class LineConstraintsE(LocalToolEnum):
    THERMOMETER = 'Thermometer'
    ROW_CYCLE_THERMOMETER = 'Row Cycle Thermometer'
    TWO_DIGIT_THERMOMETER = 'Two Digit Thermometer'

    PALINDROME = 'Palindrome'
    WHISPERS_LINE = 'Whispers Line'
    MAXIMUM_ADJACENT_DIFFERENCE_LINE = 'Maximum Adjacent Difference Line'

    RENBAN_LINE = 'Renban Line'
    DOUBLE_RENBAN_LINE = 'Double Renban Line'
    RENRENBANBAN_LINE = 'Renrenbanban Line'
    N_CONSECUTIVE_RENBAN_LINE = 'N-Consecutive Renban Line'
    KNABNER_LINE = 'Knabner Line'
    RENBAN_OR_WHISPERS_LINE = 'Renban Or Whispers Line'

    UNIQUE_VALUES_LINE = 'Unique Values Line'
    REGION_SUM_LINE = 'Region Sum Line'
    ARITHMETIC_SEQUENCE_LINE = 'Arithmetic Sequence Line'
    SUM_LINE = 'Sum Line'
    TWO_DIGIT_SUM_LINE = 'Two Digit Sum Line'
    XV_LINE = 'XV Line'
    AT_LEAST_X_LINE = 'At Least X Line'
    SUPERFUZZY_ARROW = 'Superfuzzy Arrow'
    N_CONSECUTIVE_FUZZY_SUM_LINE = 'N-Consecutive Sum Line'
    ADJACENT_CELL_SUM_IS_PRIME_LINE = 'Adjacent Cell Sum Is Prime Line'
    PRODUCT_LINE = 'Product Line'
    ADJACENT_MULTIPLES_LINE = 'Adjacent Multiples Line'
    RED_CARPET = "Red Carpet"
    ADJACENT_CELLS_ARE_CONSECUTIVE_OR_RATIO_LINE = "Adjacent Cells Are Consecutive Or Ratio Line"
    ADJACENT_DIFF_IS_AT_LEAST_X_OR_ADJACENT_SUM_IS_AT_MOST_X_LINE = "Adjacent Difference Is At Least X or Adjacent Sum Is At Most X Line"

    SAME_PARITY_LINE = 'Same Parity Line'
    MODULAR_LINE = 'Modular Line'
    UNIMODULAR_LINE = 'Unimodular Line'
    MODULAR_OR_UNIMODULAR_LINE = 'Modular Or Unimodular Line'
    ODD_EVEN_OSCILLATOR_LINE = 'Odd Even Oscillator Line'
    HIGH_LOW_OSCILLATOR_LINE = 'High Low Oscillator Line'
    ENTROPIC_LINE = 'Entropic Line'
    ENTROPIC_OR_MODULAR_LINE = 'Entropic Or Modular Line'

    INDEXING_COLUMN_IS_X_LINE = 'Indexing Column Is X Line'
    INDEXING_ROW_IS_X_LINE = 'Indexing Row Is X Line'

    REPEATED_DIGITS_LINE = 'Repeated Digits Line'
    N_REPEATED_DIGITS_LINE = 'N-Repeated Digits Line'

    BETWEEN_LINE = 'Between Line'
    LOCKOUT_LINE = 'Lockout Line'
    TIGHTROPE_LINE = 'Tightrope Line'
    PARITY_COUNT_LINE = 'Parity Count Line'
    DOUBLE_ARROW_LINE = 'Double Arrow Line'
    PRODUCT_OF_ENDS_EQUALS_SUM_OF_LINE = 'Product Of Ends Equals Sum Of Line'

    DOUBLERS_BETWEEN_LINE = 'Doublers Between Line'

    KILLER_CAGE_VALUES_FORM_PALINDROME_LINE = 'Killer Cage Values Form Palindrome Line'
    KILLER_CAGE_VALUES_FORM_RENBAN_LINE = 'Killer Cage Values Form Renban Line'
    DOUBLERS_DOUBLE_ARROW_LINE = 'Doublers Double Arrow Line'
    DOUBLERS_REGION_SUM_LINE = 'Doublers Region Sum Line'
    DOUBLERS_THERMOMETER = 'Doublers Thermometer'
    HOT_COLD_THERMOMETER = 'Hot Cold Thermometer'
    YIN_YANG_REGION_SUM_LINE = 'Yin Yang Region Sum Line'
    YIN_YANG_CALIFORNIAN_MOUNTAIN_SNAKE = 'Yin Yang Californian Mountain Snake'


class ArrowConstraintsE(LocalToolEnum):
    ARROW = 'Arrow'
    AVERAGE_ARROW = 'Average Arrow'

    VAMPIRE_PREY_ARROW = 'Vampire Prey Arrow'
    DOUBLERS_MULTIPLIER_ARROW = 'Doublers Multiplier Arrow'
    YIN_YANG_ARROW = 'Yin Yang Arrow'


class CageConstraintsE(LocalToolEnum):
    KILLER_CAGE = 'Killer Cage'
    SUM_CAGE = 'Sum Cage'
    KILLER_CAGE_LOOK_AND_SAY = 'Killer Cage Look And Say'
    PARITY_BALANCE_KILLER_CAGE = 'Parity Balance Killer Cage'
    DIVISIBLE_KILLER_CAGE = 'Divisible Killer Cage'
    SPOTLIGHT_CAGE = 'Spotlight Cage'
    PUTTERIA_CAGE = 'Putteria Cage'
    AQUARIUM_CAGE = 'Aquarium Cage'
    PRIME_DOMINOES_CAGE = "Prime Dominoes Cage"
    NO_PRIME_DOMINOES_CAGE = "No Prime Dominoes Cage"
    CAGE_AS_A_NUMBER = "Cage As A Number"
    SUJIKEN_REGION = 'Sujiken Region'

    YIN_YANG_BREAKEVEN_KILLER_CAGE = 'Yin Yang Breakeven Killer Cage'
    YIN_YANG_ANTITHESIS_KILLER_CAGE = 'Yin Yang Antithesis Killer Cage'
    DOUBLERS_KILLER_CAGE = 'Doublers Killer Cage'
    NEGATORS_KILLER_CAGE = 'Negators Killer Cage'
    HOT_COLD_KILLER_CAGE = 'Hot Cold Killer Cage'
    FOUNTAIN_KILLER_CAGE = 'Fountain Killer Cage'
    MULTIPLIERS_KILLER_CAGE = 'Multipliers Killer Cage'


class TwoRegionsConstraintsE(LocalToolEnum):
    CLONES = 'Clones'


class OutsideEdgeConstraintsE(LocalToolEnum):
    SANDWICH_SUM = 'Sandwich Sum'
    X_SUM = 'X-Sum'
    SHORTSIGHTED_X_SUM = 'Shortsighted X-Sum'
    SHIFTED_X_SUM = 'Shifted X-Sum'
    X_SUM_SKYSCRAPERS = 'X-Sum Skyscrapers'
    BROKEN_X_SUM = 'Broken X-Sum'
    BATTLEFIELD = 'Battlefield'
    SKYSCRAPERS = 'Skyscrapers'
    X_INDEX = 'X-Index'
    RISING_STREAK = 'Rising Streak'
    ROW_OR_COLUMN_RANK = 'Row Or Column Rank'
    FIRST_SEEN_ODD_EVEN = 'First Seen Odd/Even'

    OUTSIDE_EDGE_YIN_YANG_SUM_OF_SHADED = 'Outside Edge Yin Yang Sum Of Shaded'
    X_SUM_REGION_BORDERS = 'X-Sum Region Borders'


class OutsideCornerConstraintsE(LocalToolEnum):
    LITTLE_KILLER_SUM = 'Little Killer Sum'
    LITTLE_KILLER_LOOK_AND_SAY = 'Little Killer Look And Say'
    LITTLE_KILLER_REGION_SUM_PRODUCT = 'Little Killer Region Sum Product'
    X_OMIT_LITTLE_KILLER_SUM = 'X-Omit Little Killer Sum'

    NEGATORS_LITTLE_KILLER_SUM = 'Negators Little Killer Sum'


class ValuedGlobalConstraintsE(LocalToolEnum):
    FORBIDDEN_ORTHOGONALLY_ADJACENT_SUM = 'Forbidden Orthogonally Adjacent Sum'
    FORBIDDEN_ORTHOGONALLY_ADJACENT_SUM_MULTIPLE = 'Forbidden Orthogonally Adjacent Sum Multiple'
    MINIMUM_ORTHOGONALLY_ADJACENT_SUM = 'Minimum Orthogonally Adjacent Sum'
    MINIMUM_ORTHOGONALLY_ADJACENT_DIFFERENCE = 'Minimum Orthogonally Adjacent Difference'
    MAXIMUM_ORTHOGONALLY_ADJACENT_DIFFERENCE = 'Maximum Orthogonally Adjacent Difference'
    MINIMUM_DIAGONALLY_ADJACENT_DIFFERENCE = 'Minimum Diagonally Adjacent Difference'


class DoubleValuedGlobalConstraintsE(LocalToolEnum):
    FORBIDDEN_ORTHOGONAL_ADJACENCIES = 'Forbidden Orthogonal Adjacencies'


class RCConstraintsE(LocalToolEnum):
    ROTATIONALLY_SYMMETRIC_GALAXY = 'Rotationally Symmetric Galaxy'
    BALANCED_LOOP_CELL_OR_BORDER = 'Balanced Loop Cell Or Border'


class CosmeticToolsE(LocalToolEnum):
    COSMETIC_CELL = 'Cosmetic Cell'
    COSMETIC_EDGE = 'Cosmetic Edge'
    COSMETIC_CORNER = 'Cosmetic Corner'

    COSMETIC_LINE = 'Cosmetic Line'
    COSMETIC_ARROW = 'Cosmetic Arrow'

    COSMETIC_CAGE = 'Cosmetic Cage'


tool_enums = {k: v for (k, v) in globals().items() if inspect.isclass(
    v) and issubclass(v, ToolEnum)}

global_tool_enums = {k: v for (k, v) in globals().items() if inspect.isclass(
    v) and issubclass(v, BoolToolEnum)}

local_tool_enums = {k: v for (k, v) in globals().items() if inspect.isclass(
    v) and issubclass(v, LocalToolEnum)}


def constraintFromToolId(id: str) -> ToolEnum | None:
    for tool_enum in tool_enums.values():
        for entry in tool_enum:
            if id == entry.value:
                return entry
    return None


def toolConstraintGen() -> Iterable[ToolEnum]:
    for tool_enum in tool_enums.values():
        for entry in tool_enum:
            yield entry
    return


def localToolConstraintGen() -> Iterable[LocalToolEnum]:
    for tool_enum in local_tool_enums.values():
        for entry in tool_enum:
            yield entry
    return


def globalToolConstraintGen() -> Iterable[BoolToolEnum]:
    for tool_enum in global_tool_enums.values():
        for entry in tool_enum:
            yield entry
    return


def isToolOfType(tool: ToolEnum, tool_class: Type[ToolEnum]) -> bool:
    return any(tool == tool_b for tool_b in tool_class)


def isStrOfToolEnumType(tool: str, tool_class: Type[ToolEnum]) -> bool:
    return any(tool == tool_b.value for tool_b in tool_class)


if __name__ == "__main__":
    tool = "Difference"

    # for res in toolConstraintGen():
    #     print(res, res.value)

    res = constraintFromToolId(tool)
    print(res)

    # res = isLocalToolOfType(tool, EdgeConstraintsE)
    # print(res)
