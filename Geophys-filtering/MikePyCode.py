# From "\\prod.lan\active\proj\futurex\Common\Working\Mike\GitHub\mjb_work_code\OracleLoadingFunctions\OracleLoadingFunctions.py"

def estimate_max_induction_clip(df):
    # BAsed on the criteria from KP the logs can be cut below where the deep induction channel
    # starts returning nulls
    return df[df['DEEP_INDUCTION'].notna()].iloc[-1].name

# Also from "\\prod.lan\active\proj\futurex\Common\Working\Mike\GitHub\mjb_work_code\OracleLoadingFunctions\OracleLoadingFunctions.py"
# Need to investigate, possibly related to filtering gamma, induction

def combination(n, r): # calculation of combinations, n choose k
    return int((math.factorial(n)) / ((math.factorial(r)) * math.factorial(n - r)))   

def pascals_triangle(rows):
    result = [] 
    for count in range(rows): # start at 0, up to but not including rows number.
        # this is really where you went wrong:
        row = [] # need a row element to collect the row in
        for element in range(count + 1): 
            # putting this in a list doesn't do anything.
            # [pascals_tri_formula.append(combination(count, element))]
            row.append(combination(count, element))
        result.append(row)
        # count += 1 # avoidable
    return result[rows-1]

def binom_filter(x, kernel):
    return np.mean(np.convolve(x, kernel, 'same'))
    
def run_filter(series, window, min_periods, filter):
    if filter == 'median':
        return series.rolling(window = window, min_periods = min_periods).median()
    elif filter == 'binomial':
        kernel = pascals_triangle(window)/np.sum(pascals_triangle(window))
        return series.rolling(window = window, min_periods = min_periods).apply(binom_filter, args = (kernel,), raw=True)
    elif filter == 'mean':
        return series.rolling(window = window, min_periods = min_periods).mean() 
    else:
        return series 
