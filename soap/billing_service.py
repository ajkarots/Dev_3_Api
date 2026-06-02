from spyne import Application, rpc, ServiceBase, Integer, Unicode, ComplexModel
from spyne import Application, rpc, ServiceBase, Integer, Unicode, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

class RespuestaFactura(ComplexModel):
    estado = Unicode
    mensaje = Unicode
    clave_acceso = Unicode

class FacturacionService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def ValidarFactura(ctx, xmlFactura):
        return "VALIDADA"

    @rpc(Integer, _returns=RespuestaFactura)
    def GenerarFacturaXML(ctx, idCompra):
        return RespuestaFactura(
            estado="VALIDADA",
            mensaje="Factura generada correctamente",
            clave_acceso=f"FAC-2026-{idCompra:05d}"
        )

    @rpc(Integer, _returns=Unicode)
    def ConsultarComprobante(ctx, idCompra):
        return f"Comprobante para la compra {idCompra} autorizado por el SRI."

soap_app = Application(
    [FacturacionService],
    tns='techstore.facturacion.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_soap_app = WsgiApplication(soap_app)