import sympy
from sympy import *
from ui.utils import *
from django.db import connection, transaction


class Op:
    LT = -1
    GT = 1
    op_code = 0

    def is_lt(self):
        return self.op_code == self.LT

    def is_gt(self):
        return self.op_code == self.GT

    def __init__(self, op_str):
        if op_str == '<':
            self.op_code = self.LT
        elif op_str == '>':
            self.op_code = self.GT

    def __str__(self):
        if self.is_lt():
            return '<'
        else:
            return '>'

    def flip(self):
        self.op_code *= -1


class SymbolicUtils:
    @classmethod
    def encode_tag(cls, key):
        return Symbol('s' + str(key))

    @classmethod
    def decode_tag(cls, symbol):
        return int(str(symbol)[1:])

    @classmethod
    def get_mvp_term(cls, ineqn):
        """
        Scans through formula and picks out symbol with largest ordinal tag.
        Returns that symbol's coefficient and the symbol itself as a pair.
        If there are no symbols in the expression (i.e. it is a number),
        then return None
        """
        if isinstance(ineqn.expand(), sympy.numbers.Number):
            return None
        if isinstance(ineqn.expand(), sympy.mul.Mul):
            assert len(ineqn.args) == 2
            return ineqn.as_two_terms()
        assert isinstance(ineqn, sympy.add.Add)
        mvp_tag = -1
        mvp_sym = None
        for term in ineqn.as_ordered_terms():
            for factor in term.as_ordered_factors():
                if isinstance(factor, sympy.symbol.Symbol):
                    tag = cls.decode_tag(factor)
                    if tag > mvp_tag:
                        mvp_tag = tag
                        mvp_sym = factor

        return (ineqn.coeff(mvp_sym), mvp_sym,)

    @classmethod
    def extract_mvp(cls, ineqn):
        """
        rewrite an equation of the form a*l1 + b*l2 + c*l3 > 0
        to be (a*l1 + b*l2)/-c < l3
        """
        mvp_term = cls.get_mvp_term(ineqn)
        lhs = 0
        rhs = ineqn.as_expr()
        op = Op('<')
        if mvp_term is not None:
            coef, symbol = mvp_term
            # subtract mvp_term from both sides
            lhs -= coef * symbol
            rhs -= coef * symbol
            # divide both sides by -coef
            lhs /= -coef
            rhs /= -coef
            if -coef < 0:
                op.flip()
            return (lhs.as_expr(), str(op), rhs.as_expr(),)
        return None


class StaticPricer:
    """
    """
    def __init__(self, domain_id):
        self.domain_id = domain_id

    @transaction.commit_on_success
    def get_level_number_extrema(self):
        cmd = """ SELECT MIN(level_number) as min, MAX(level_number) as max
                  FROM ui_level
                  WHERE domain_id = %s """
        cursor = connection.cursor()
        cursor.execute(cmd, (self.domain_id,))
        res = dictfetchall(cursor)
        assert len(res) == 1
        return res[0]

    @transaction.commit_on_success
    def calculate_level_histograms(self):
        """
        Iterate through alloction records, grouping by allocation id
        sorting users into bucket based on level number
        """
        histograms = []
        cmd = """ SELECT a.domain_id, a.allocation_id, a.user_level,
                         a.user_id, a.accuracy, c.confidence_score
                  FROM allocations a, alloc_conf_scores c
                  WHERE a.domain_id = %s AND a.domain_id = c.domain_id
                    AND a.allocation_id = c.allocation_id
                  ORDER BY c.confidence_score DESC, a.domain_id, a.allocation_id"""
        cursor = connection.cursor()
        cursor.execute(cmd, (self.domain_id,))
        curr_id = -1
        histogram = {}
        for row in dictfetchall(cursor):
            alloc_id = row['allocation_id']
            if curr_id != alloc_id:
                if 'alloc_id' in histogram:
                    histograms.append(dict(histogram))
                histogram = {'alloc_id': alloc_id, 'conf_score': row['confidence_score']}
                curr_id = alloc_id
            users = histogram.setdefault(row['user_level'], [])
            # user_info = {}
            # for key in ['user_id', 'accuracy']:
            #     user_info[key] = row[key]
            # users.append(user_info)
            users.append(1)
        return histograms

    @staticmethod
    def get_coefs(histo):
        """
        Pluck out the coefficients of the pricing function.
        """
        coefs = {}
        for key in histo:
            if isinstance(histo[key], list):
                coefs[key] = len(histo[key])
        return coefs

    def create_pricing_ineqns(self):
        """
        For each pair of allocations A[x], A[x+1]
        Create formulas representing total price
        Find A[x] - A[x+1]
        Rewrite in terms of highest valued variable
        Hash equation, update histogram
        """
        histograms = self.calculate_level_histograms()
        ineqns = {}
        penultimate = len(histograms) - 1
        for x in range(penultimate):
            formulas = [0, 0]
            for y in range(2):
                histo = histograms[x + y]
                coefs = self.get_coefs(histo)
                for key in coefs:
                    curr_symbol = SymbolicUtils.encode_tag(key)
                    formulas[y] += int(coefs[key]) * curr_symbol
            new_formula = formulas[0] - formulas[1]
            ineqn = SymbolicUtils.extract_mvp(new_formula)
            if ineqn is not None:
                cnt = ineqns.setdefault(ineqn, 0)
                ineqns[ineqn] = cnt + 1
        return ineqns

    def calculate_prices(self):
        ineqns = self.create_pricing_ineqns()
        # reformat histogram of inequations into list of tuples
        # to make them sortable.
        ineqns_refmt = []
        for key in ineqns:
            ineqns_refmt.append((ineqns[key], key,))
        ineqns_refmt.sort(key=lambda x: x[0], reverse=True)
        # partition inequations
        parts = {}
        for item in ineqns_refmt:
            freq, ineqn = item
            items = parts.setdefault(ineqn[0], [])
            items.append(item)
        # check to see that all symbols have at least one
        # constraint. if not, inject a trivial constraint.
        extrema = self.get_level_number_extrema()
        for l in range(extrema['min'], 1 + extrema['max']):
            sym = SymbolicUtils.encode_tag(l)
            if sym not in parts:
                if l == 0:
                    rhs = 0
                else:
                    rhs = SymbolicUtils.encode_tag(l - 1)
                parts[sym] = [(0, (sym, '>', rhs))]
        symbols = parts.keys()
        symbols.sort(key=lambda x: SymbolicUtils.decode_tag(x))
        bounds = {}
        vals = {}
        prev = 0.0
        incr = 1.0
        satisfied = []
        unsatisfied = []
        for sym in symbols:
            interval = bounds.setdefault(sym, [prev, oo])
            # always give the first level a constant price
            if SymbolicUtils.decode_tag(sym) == 1:
                prev = vals[sym] = incr
                continue
            for eqn in parts[sym]:
                lhs, op, rhs = eqn[1]
                rhs = float(rhs.evalf(subs=vals))
                if op == '>':
                    lower = max(interval[0], rhs)
                    if lower >= interval[1]:
                        unsatisfied.append(eqn)
                    else:
                        interval[0] = lower
                        satisfied.append(eqn)
                elif op == '<':
                    upper = min(interval[1], rhs)
                    if upper <= interval[0]:
                        unsatisfied.append(eqn)
                    else:
                        interval[1] = upper
                        satisfied.append(eqn)
            if interval[1] is not oo:
                prev = vals[sym] = (interval[0] + interval[1]) / 2
            else:
                prev = vals[sym] = interval[0] + incr
        total_sat = 0
        for x in satisfied:
            total_sat += x[0]
        total_unsat = 0
        for x in unsatisfied:
            total_unsat += x[0]
        response = {}
        response['total_sat'] = total_sat
        response['total_unsat'] = total_unsat
        response['prices'] = vals
        return response
