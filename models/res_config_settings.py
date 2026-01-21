from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dbd_api_url = fields.Char(
        string="DBD API URL", 
        default="https://opendata.dbd.go.th/th/api/3/action/datastore_search",
        config_parameter='om_dbd_search.api_url'
    )
    dbd_resource_id = fields.Char(
        string="Resource ID", 
        default="f008dbbf-ddfa-4e3a-bac4-358a1a2b9853",
        config_parameter='om_dbd_search.resource_id'
    )
    dbd_api_token = fields.Char(
        string="API Key (Token)", 
        config_parameter='om_dbd_search.api_token'
    )