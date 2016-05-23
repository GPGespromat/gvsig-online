# -*- coding: utf-8 -*-

'''
    gvSIG Online.
    Copyright (C) 2007-2015 gvSIG Association.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

'''
@author: Javier Rodrigo <jrodrigo@scolab.es>
'''

from django.shortcuts import render_to_response, RequestContext, HttpResponse
from django.contrib.auth.decorators import login_required
from gvsigol_services.models import Layer, Datastore, Workspace
from gvsigol_services.backend_mapservice import backend as mapservice_backend
from models import Style, StyleLayer, Rule, Symbolizer, StyleRule, Library
from gvsigol_symbology.sld_utils import get_sld_style, get_sld_filter_operations
from gvsigol_symbology import services
from django.utils.translation import ugettext as _
from gvsigol_auth.utils import admin_required
from utils import sortFontsArray
import utils
import json

  
@login_required(login_url='/gvsigonline/auth/login_user/')
@admin_required
def unique_symbol_add(request, layer_id):
    fields = services.get_fields(layer_id, request.session)
    feature_type = services.get_feature_type(fields)
    sld_filter_values = services.get_sld_filter_values()
    alphanumeric_fields = services.get_alphanumeric_fields(fields)
       
    supported_fonts_str = mapservice_backend.getSupportedFonts(request.session)
    supported_fonts = json.loads(supported_fonts_str)
    sorted_fonts = sortFontsArray(supported_fonts.get("fonts"))
    
    layer = Layer.objects.get(id=int(layer_id))
    index = len(StyleLayer.objects.filter(layer=layer))
                      
    response = {
        'featureType': feature_type,
        'fields': json.dumps(fields), 
        'alphanumeric_fields': json.dumps(alphanumeric_fields),
        'sldFilterValues': json.dumps(sld_filter_values),
        'fonts': sorted_fonts,
        'layer_id': layer_id,
        'style_name': layer.name + '_' + str(index),
        'libraries': Library.objects.all()
    }
   
    return render_to_response('unique_symbol_add.html', response, context_instance=RequestContext(request))

@login_required(login_url='/gvsigonline/auth/login_user/')
@admin_required
def unique_symbol_update(request, layer_id, style_id):  
    if request.method == 'POST':
        style_data = request.POST['style_data']
        json_data = json.loads(style_data)
        
        style = Style.objects.get(id=int(style_id))
        layer = Layer.objects.get(id=int(layer_id))
        
        style.title = json_data.get('title')
        style.is_default = json_data.get('is_default')
        style.save()
        
        if style.is_default:
            layer_styles = StyleLayer.objects.filter(layer=layer)
            for ls in layer_styles:
                s = Style.objects.get(id=ls.style.id)
                s.is_default = False
            datastore = layer.datastore
            workspace = datastore.workspace
            mapservice_backend.setLayerStyle(workspace.name+":"+layer.name, style.name, request.session)
        
        json_rule = json_data.get('rule')
        style_rule = StyleRule.objects.get(style=style)
        minscale = json_rule.get('minscale')
        maxscale = json_rule.get('maxscale')
        #style_rule.rule.minscale = float(minscale),
        #style_rule.rule.maxscale = float(maxscale),
        #style_rule.rule.save();
        
        for s in Symbolizer.objects.filter(rule=style_rule.rule):
            s.delete()
            
        for sym in json_data.get('symbolizers'):    
            symbolizer = Symbolizer(
                rule = style_rule.rule,
                type = sym.get('type'),
                sld = sym.get('sld'),
                json = sym.get('json'),
                order = int(sym.get('order'))
            )
            symbolizer.save()
             
        sld_body = get_sld_style(layer_id, style.id, request.session)
        if mapservice_backend.updateStyle(style.name, sld_body, request.session): 
            return HttpResponse(json.dumps({'success': True}, indent=4), content_type='application/json')
        else:
            return HttpResponse(json.dumps({'success': False}, indent=4), content_type='application/json')
        
    else:
        style = Style.objects.get(id=int(style_id))
        layer = Layer.objects.get(id=int(layer_id))
        
        datastore = Datastore.objects.get(id=layer.datastore_id)
        workspace = Workspace.objects.get(id=datastore.workspace_id)           
        split_wms_url = workspace.wms_endpoint.split('//')
        authenticated_wms_url = split_wms_url[0] + '//' + request.session['username'] + ':' + request.session['password'] + '@' + split_wms_url[1]
        layer_url = authenticated_wms_url
        
        fields = services.get_fields(layer_id, request.session)
        feature_type = services.get_feature_type(fields)
        sld_filter_values = services.get_sld_filter_values()
        alphanumeric_fields = services.get_alphanumeric_fields(fields)
           
        supported_fonts_str = mapservice_backend.getSupportedFonts(request.session)
        supported_fonts = json.loads(supported_fonts_str)
        sorted_fonts = sortFontsArray(supported_fonts.get("fonts"))
                
        style_rule = StyleRule.objects.get(style=style)
        r = Rule.objects.get(id=int(style_rule.rule.id))
        symbolizers = []
        for s in Symbolizer.objects.filter(rule=r).order_by('order'):
            symbolizers.append({
                'type': s.type,
                'json': s.json
            })
        rule = {
            'id': r.id,
            'name': r.name,
            'title': r.title,
            'minscale': r.minscale,
            'maxscale': r.maxscale,
            'order': r.order,
            'type': r.type,
            'symbolizers': symbolizers
        }
                            
        response = {
            'featureType': feature_type,
            'fields': json.dumps(fields), 
            'alphanumeric_fields': json.dumps(alphanumeric_fields),
            'sldFilterValues': json.dumps(sld_filter_values),
            'fonts': sorted_fonts,
            'layer_id': layer_id,
            'layer_url': layer_url,
            'layer_name': workspace.name + ':' + layer.name,
            'libraries': Library.objects.all(),
            'style': style,
            'minscale': r.minscale,
            'maxscale': r.maxscale,
            'rule': json.dumps(rule)
            
        }
        return render_to_response('unique_symbol_update.html', response, context_instance=RequestContext(request))