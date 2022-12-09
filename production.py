# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from decimal import Decimal
from trytond.i18n import gettext
from trytond.modules.production.exceptions import CostWarning

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

            sum_ = Decimal(0)
            for output in production.outputs:
                product = output.product
                list_price = product.list_price_used
                if list_price is None:
                    warning_name = Warning.format(
                        'production_missing_list_price', [product])
                    if Warning.check(warning_name):
                        raise CostWarning(warning_name,
                            gettext(
                                'production.msg_missing_product_list_price',
                                product=product.rec_name,
                                production=production.rec_name))
                    continue
                product_price = (Decimal(str(output.quantity))
                    * Uom.compute_price(
                        product.default_uom, list_price, output.uom))
                sum_ += product_price
            if not sum_ and production.product:
                for output in production.outputs:
                    if output.product == production.product:
                        quantity = Uom.compute_qty(
                            output.uom, output.quantity,
                            output.product.default_uom, round=False)
                        quantity = Decimal(str(quantity))
                        sum_ += quantity
            if production.company.currency.is_zero(production.cost - sum_):
                continue

            unit_price = production.cost / Decimal(
                str(production.product_output_quantity))
            for output in production.outputs:
                if output.product == production.product:
                    output.unit_price = Uom.compute_price(
                        production.uom, unit_price, output.uom).quantize(digit)
                    moves.append(output)
        Move.save(moves)
