-- TODO 4: este mart devuelve una fila por pedido. Agregalo para que
-- responda cuanto se vendio por ciudad: numero de pedidos y monto total.
select *
from {{ ref('int_pedidos_con_cliente') }}
