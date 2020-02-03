# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from decimal import Decimal

__all__ = ['Production']


class Production(metaclass=PoolMeta):
    __name__ = 'production'

    @property
    def product_output_quantity(self):
        return Decimal(sum([x.quantity for x in self.outputs
                if x.product == getattr(self, 'product', None) and
                    x.quantity is not None]))

    @classmethod
    def set_cost(cls, productions):
        pool = Pool()
        Uom = pool.get('product.uom')
        Move = pool.get('stock.move')
        super().set_cost(productions)

        digits = Move.unit_price.digits
        digit = Decimal(str(10 ** -digits[1]))
        moves = []
        for production in productions:
            if not production.quantity or not production.uom:
                continue
            if production.company.currency.is_zero(
                    production.cost - production.output_cost):
                continue
            unit_price = production.cost / Decimal(
                str(production.product_output_quantity))
            for output in production.outputs:
                if output.product == production.product:
                    output.unit_price = Uom.compute_price(
                        production.uom, unit_price, output.uom).quantize(digit)
                    moves.append(output)
        Move.save(moves)
