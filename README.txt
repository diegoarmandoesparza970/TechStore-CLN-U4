TECHSTORE U4 - NUCLEO DE NEGOCIO
Actividad 4 - Componentes de logica de negocios - Equipo 1 - Grupo 002

Implementacion del nucleo de negocio de TechStore, una tienda ficticia, con
Domain-Driven Design. El sistema carga clientes, productos y pedidos desde
archivos CSV, calcula descuentos con el patron Specification, controla el ciclo
de vida de cada pedido con una maquina de estados y expone parte de esa logica
mediante una API REST con FastAPI.

Todo funciona EN MEMORIA: no hay base de datos, asi que al cerrar el programa o
reiniciar la API los pedidos vuelven a su estado inicial (DRAFT).


INTEGRANTES
  2025292  Jose Angel Leal Sifuentes
  2019069  Cristopher Led Juarez Luna
  1908457  Diego Armando Esparza Flores


ESTRUCTURA DEL PROYECTO
  datos/                   5 CSV: clientes, productos, pedidos,
                           detalle_pedidos, escenarios
  cargar_csv.py            convierte los CSV en objetos del dominio
  ejecutar_escenarios.py   ejecuta E01-E15 y genera
                           docs/bitacora_escenarios.md
  app/
    domain.py              Money, Customer, OrderItem, Order, DomainEvent y
                           excepciones
    specifications.py      Specification (AND/OR/NOT), reglas de descuento y
                           discount_rate()
    api.py                 API REST con FastAPI
  tests/
    test_domain.py         pruebas del dominio (5)
    test_escenarios.py     pruebas de E01-E15 y de reglas de borde (28)
  docs/
    bitacora_escenarios.md
  requirements.txt


INSTALACION
Requiere Python 3.11 o superior.

  python -m venv .venv
  .venv\Scripts\Activate.ps1          (Windows PowerShell)
  .venv\Scripts\activate.bat          (Windows CMD)
  source .venv/bin/activate           (macOS / Linux)
  python -m pip install -r requirements.txt

Si el comando "python" no se reconoce en Windows, prueba con "py" o con la ruta
completa del ejecutable de Python.


EJECUCION
Todos los comandos se ejecutan desde la carpeta raiz del proyecto, la que
contiene app/ y datos/.

  python cargar_csv.py                     muestra los 16 pedidos (todos DRAFT)
  python ejecutar_escenarios.py            corre E01-E15 y escribe la bitacora
  python -m pytest -q                      corre las 33 pruebas automaticas
  python -m uvicorn app.api:app --reload   levanta la API

Con la API en marcha, la documentacion interactiva (Swagger) esta en
http://127.0.0.1:8000/docs


REGLAS DE NEGOCIO
  - Money es inmutable, usa Decimal, rechaza montos negativos o no finitos y
    solo suma monedas iguales.
  - OrderItem exige un SKU no vacio y una cantidad mayor que 0. El subtotal es
    precio x cantidad.
  - Un pedido admite como maximo 20 unidades (suma de cantidades, no numero de
    renglones).
  - Solo se agregan articulos mientras el pedido esta en DRAFT y solo en MXN.
  - Descuento del 10 %: cliente VIP y total mayor a 500 y al menos 4 unidades
    y sin promocion activa.
  - Descuento del 5 %: total mayor a 5000 y sin promocion activa.
  - Si se cumplen ambas reglas, gana la del 10 %. Con una promocion activa no
    hay descuento.
  - Los umbrales de monto son estrictos (>): un total exacto de 500 o de 5000
    no activa el descuento.
  - No se controla inventario; la existencia del catalogo es solo informativa.

La prioridad entre descuentos se resuelve en un solo lugar: discount_rate(order)
en app/specifications.py.


MAQUINA DE ESTADOS Y DOMAIN EVENTS

  DRAFT --confirm()--> CONFIRMED --ship(guia)--> SHIPPED --deliver()--> DELIVERED
                           |                        |
                           |                        +--return_order()--> RETURNED
                           |
                           +--cancel(motivo)--> CANCELLED

  Operacion         Requisitos                                   Evento
  ----------------  -------------------------------------------  --------------
  confirm()         Estado DRAFT, con articulos y cliente activo OrderConfirmed
  ship(guia)        Estado CONFIRMED y guia no vacia             OrderShipped
  cancel(motivo)    Estado CONFIRMED y motivo no vacio           OrderCancelled
  deliver()         Estado SHIPPED                               OrderDelivered
  return_order()    Estado SHIPPED                               OrderReturned

En cada metodo primero se validan las condiciones, despues se cambia el estado
y, al final, se registra el evento. Por eso una operacion invalida nunca cambia
el estado ni deja eventos registrados.


API REST
  Metodo  Ruta                          Descripcion                  Respuestas
  ------  ----------------------------  ---------------------------  ------------------
  GET     /orders/{order_id}            Consulta un pedido: id,      200, 404
                                        estado, unidades y total
  POST    /orders/{order_id}/confirm    Confirma el pedido           200, 404, 409, 422
  POST    /orders/{order_id}/ship       Cuerpo:                      200, 404, 409, 422
                                        {"tracking_number": "..."}
  POST    /orders/{order_id}/cancel     Cuerpo: {"reason": "..."}    200, 404, 409, 422

Codigos de error:
  404  El pedido no existe.
  409  La transicion no esta permitida desde el estado actual
       (InvalidOrderTransition).
  422  Los datos violan una regla del negocio, como un cliente inactivo, un
       pedido vacio o una guia vacia (InvalidOrderData).

Los identificadores de pedido llevan la letra O mayuscula (por ejemplo O001),
no el numero cero.


PRUEBAS
Hay 33 pruebas con pytest:
  - tests/test_domain.py: 5 pruebas del dominio.
  - tests/test_escenarios.py: 28 pruebas, una por cada escenario E01-E15 mas
    reglas de borde (umbrales de 500 y 5000, limite de 20 unidades, estados
    finales, validaciones de Money y OrderItem).

  python -m pytest -v

Los 15 escenarios (datos/escenarios.csv) se ejecutan con ejecutar_escenarios.py.
Los descuentos se calculan con las Specifications y no estan escritos a mano; el
resultado queda en docs/bitacora_escenarios.md.


ALCANCE
Quedan fuera de esta practica la persistencia en base de datos y el control de
inventario.
