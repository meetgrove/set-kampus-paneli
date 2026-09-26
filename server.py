#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SET Kampüse Hoş Geldin Fest — 7/24 Kesintisiz Bulut Sunucusu (Unified Cloud Server)
Tekirdağ Namık Kemal Üniversitesi | Sportif ve Sosyal Etkinlikler Topluluğu (SET)

Bu sunucu hem 'SET Ekip Koordinasyon Paneli'ni hem de 'Festival Kroki ve Stand Yerleşim Paneli'ni
tek bir port ve tek bir kalıcı bulut linki (Render.com, Railway, VPS vb.) üzerinden 7/24 sunar.
"""

import os
import sys
import json
import socket
import time
import io
import csv
import threading
import urllib.request
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_EKIP = os.path.join(BASE_DIR, 'data.json')
DATA_KROKI = os.path.join(BASE_DIR, 'kroki', 'kroki_data.json')
HTML_EKIP = os.path.join(BASE_DIR, 'index.html')
HTML_KROKI = os.path.join(BASE_DIR, 'kroki', 'index.html')

PORT = int(os.environ.get('PORT', 5050))
LOCK_EKIP = threading.Lock()
LOCK_KROKI = threading.Lock()

def load_ekip_data():
    with LOCK_EKIP:
        if os.path.exists(DATA_EKIP):
            with open(DATA_EKIP, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

def save_ekip_data(data):
    with LOCK_EKIP:
        with open(DATA_EKIP, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def load_kroki_data():
    with LOCK_KROKI:
        if os.path.exists(DATA_KROKI):
            with open(DATA_KROKI, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"meta": {}, "elements": [], "strokes": [], "texts": []}

def save_kroki_data(data):
    with LOCK_KROKI:
        with open(DATA_KROKI, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

class SetUnifiedHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json_response(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def serve_file(self, file_path, content_type=None, cache_age=86400):
        if not os.path.isfile(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File Not Found')
            return

        if not content_type:
            ext = os.path.splitext(file_path)[1].lower()
            mime_map = {
                '.html': 'text/html; charset=utf-8',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.ico': 'image/x-icon',
                '.json': 'application/manifest+json' if 'manifest' in file_path else 'application/json',
                '.webmanifest': 'application/manifest+json',
                '.svg': 'image/svg+xml',
                '.js': 'application/javascript',
                '.css': 'text/css'
            }
            content_type = mime_map.get(ext, 'application/octet-stream')

        self.send_response(200)
        self.send_header('Content-Type', content_type)
        if cache_age > 0:
            self.send_header('Cache-Control', f'public, max-age={cache_age}')
        else:
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.end_headers()
        with open(file_path, 'rb') as f:
            self.wfile.write(f.read())

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # 1. Health & Heartbeat
        if path == '/health' or path == '/ping':
            self.send_json_response({
                'status': 'ok',
                'service': 'SET Kampuse Hos Geldin - 7/24 Bulut Paneli',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0-cloud'
            })
            return

        # 2. Root: Ekip Paneli
        if path == '/' or path == '/index.html':
            self.serve_file(HTML_EKIP, 'text/html; charset=utf-8', cache_age=0)
            return

        # 3. Kroki Paneli Root
        if path == '/kroki' or path == '/kroki/' or path == '/kroki/index.html':
            self.serve_file(HTML_KROKI, 'text/html; charset=utf-8', cache_age=0)
            return

        # 4. Ekip Data API
        if path == '/api/data':
            data = load_ekip_data()
            self.send_json_response(data)
            return

        # 5. Ekip Tunnel / Info API
        if path == '/api/tunnel_info':
            self.send_json_response({
                'local_ip': 'cloud',
                'port': PORT,
                'local_url': f'http://localhost:{PORT}',
                'tunnel_url': os.environ.get('RENDER_EXTERNAL_URL', ''),
                'kroki_url': './kroki/',
                'kroki_local_url': './kroki/',
                'kroki_tunnel_url': './kroki/',
                'is_cloud': True,
                'status': 'online'
            })
            return

        # 6. Kroki Data API
        if path in ['/kroki/api/data', '/api/kroki/data']:
            kdata = load_kroki_data()
            self.send_json_response(kdata)
            return

        # 7. Kroki Tunnel / Info API
        if path in ['/kroki/api/tunnel_info', '/api/kroki/tunnel_info']:
            self.send_json_response({
                'local_ip': 'cloud',
                'port': PORT,
                'local_url': './kroki/',
                'tunnel_url': os.environ.get('RENDER_EXTERNAL_URL', '') + '/kroki/',
                'is_cloud': True,
                'status': 'online'
            })
            return

        # 8. Kroki CSV Export
        if path in ['/kroki/api/export_csv', '/api/kroki/export_csv']:
            kdata = load_kroki_data()
            output = io.StringIO()
            output.write('\ufeff')
            writer = csv.writer(output, delimiter=';')
            writer.writerow([
                'No', 'İçerik / Stand Adı', 'Kategori', 'Tür',
                'Genişlik (m)', 'Derinlik (m)', 'Alan (m²)',
                'Konum X (m)', 'Konum Y (m)', 'Dönüş (°)',
                'Elektrik İhtiyacı', 'Sorumlu Kişi / İletişim', 'Notlar'
            ])
            for el in kdata.get('elements', []):
                writer.writerow([
                    el.get('num', ''),
                    el.get('name', ''),
                    el.get('category', ''),
                    el.get('type', ''),
                    str(el.get('width_m', '')).replace('.', ','),
                    str(el.get('depth_m', '')).replace('.', ','),
                    str(el.get('area_m2', '')).replace('.', ','),
                    str(el.get('x_m', '')).replace('.', ','),
                    str(el.get('y_m', '')).replace('.', ','),
                    str(el.get('rot', '0')),
                    el.get('power', ''),
                    el.get('contact', ''),
                    el.get('notes', '')
                ])
            csv_bytes = output.getvalue().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="SET_Fest_Stand_ve_Alan_Listesi.csv"')
            self.send_header('Content-Length', str(len(csv_bytes)))
            self.end_headers()
            self.wfile.write(csv_bytes)
            return

        # 9. Static Assets (Kroki subfolder)
        if path.startswith('/kroki/'):
            sub_path = path[7:] # strip '/kroki/'
            target_file = os.path.join(BASE_DIR, 'kroki', sub_path)
            if os.path.isfile(target_file):
                self.serve_file(target_file)
                return

        # 10. Static Assets (Root)
        clean_path = path.lstrip('/')
        target_file = os.path.join(BASE_DIR, clean_path)
        if os.path.isfile(target_file):
            self.serve_file(target_file)
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Sayfa Bulunamadi (404)')

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'

        try:
            req_data = json.loads(body)
        except Exception:
            req_data = {}

        # 1. Kroki Save API
        if path in ['/kroki/api/save', '/api/kroki/save']:
            req_data.setdefault('meta', {})['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_kroki_data(req_data)
            self.send_json_response({'success': True, 'message': 'Festival kroki ve saha planı kaydedildi!'})
            return

        # 2. Ekip APIs
        data = load_ekip_data()

        if path == '/api/auth/login':
            username = req_data.get('username', '').strip().lower()
            pin = str(req_data.get('pin', '')).strip()

            matched = None
            if (username == 'genel' or not username) and pin == '0000':
                matched = {
                    'username': 'genel',
                    'name': 'Genel Ekip Girişi',
                    'role': 'Saha ve Koordinasyon Ekibi',
                    'pin': '0000',
                    'department': 'Tüm Departmanlar'
                }
            else:
                for tm in data.get('team_members', []):
                    if tm.get('username', '').lower() == username and str(tm.get('pin', '')).strip() == pin:
                        matched = {
                            'username': tm['username'],
                            'name': tm['name'],
                            'role': tm['role'],
                            'department': tm.get('department', '')
                        }
                        break

            if matched:
                self.send_json_response({'success': True, 'user': matched})
            else:
                self.send_json_response({'success': False, 'error': 'Kullanıcı adı veya 4 haneli PIN hatalı!'}, 401)
            return

        elif path == '/api/tasks/claim':
            task_id = req_data.get('id')
            claimed_by = req_data.get('claimed_by', 'Ekip Üyesi')
            claimed_at = req_data.get('claimed_at', datetime.now().strftime('%d.%m %H:%M'))
            found = False
            for t in data.get('tasks', []):
                if t['id'] == task_id:
                    t['status'] = 'alindi'
                    t['claimed_by'] = claimed_by
                    t['claimed_at'] = claimed_at
                    t['updated_by'] = f"{claimed_by} (Görevi Aldı)"
                    found = True
                    break
            if found:
                save_ekip_data(data)
                self.send_json_response({'success': True, 'tasks': data.get('tasks', [])})
            else:
                self.send_json_response({'success': False, 'error': 'Görev bulunamadı'}, 404)
            return

        elif path == '/api/tasks/unclaim':
            task_id = req_data.get('id')
            user_name = req_data.get('user_name', '')
            found = False
            for t in data.get('tasks', []):
                if t['id'] == task_id:
                    t['status'] = 'yapilacak'
                    t['claimed_by'] = ''
                    t['claimed_at'] = ''
                    t['updated_by'] = f"{user_name} (Görevi Bıraktı)" if user_name else "Geri Alındı"
                    found = True
                    break
            if found:
                save_ekip_data(data)
                self.send_json_response({'success': True, 'tasks': data.get('tasks', [])})
            else:
                self.send_json_response({'success': False, 'error': 'Görev bulunamadı'}, 404)
            return

        elif path == '/api/tasks/complete':
            task_id = req_data.get('id')
            completed_by = req_data.get('completed_by', 'Ekip Üyesi')
            completed_at = req_data.get('completed_at', datetime.now().strftime('%d.%m %H:%M'))
            found = False
            for t in data.get('tasks', []):
                if t['id'] == task_id:
                    t['status'] = 'yapildi'
                    t['completed_by'] = completed_by
                    t['completed_at'] = completed_at
                    if not t.get('claimed_by'):
                        t['claimed_by'] = completed_by
                    t['updated_by'] = f"{completed_by} (Tamamladı)"
                    found = True
                    break
            if found:
                save_ekip_data(data)
                self.send_json_response({'success': True, 'tasks': data.get('tasks', [])})
            else:
                self.send_json_response({'success': False, 'error': 'Görev bulunamadı'}, 404)
            return

        elif path == '/api/tasks/uncomplete':
            task_id = req_data.get('id')
            user_name = req_data.get('user_name', '')
            found = False
            for t in data.get('tasks', []):
                if t['id'] == task_id:
                    t['status'] = 'alindi' if t.get('claimed_by') else 'yapilacak'
                    t['completed_by'] = ''
                    t['completed_at'] = ''
                    t['updated_by'] = f"{user_name} (Tamamlanmayı Geri Aldı)" if user_name else "Geri Alındı"
                    found = True
                    break
            if found:
                save_ekip_data(data)
                self.send_json_response({'success': True, 'tasks': data.get('tasks', [])})
            else:
                self.send_json_response({'success': False, 'error': 'Görev bulunamadı'}, 404)
            return

        elif path == '/api/tasks/toggle':
            task_id = req_data.get('id')
            user_name = req_data.get('user_name', '')
            found = False
            for t in data.get('tasks', []):
                if t['id'] == task_id:
                    if t.get('status') == 'yapildi':
                        t['status'] = 'alindi' if t.get('claimed_by') else 'yapilacak'
                        t['completed_by'] = ''
                        t['updated_by'] = f"{user_name} (Geri Aldı)" if user_name else "Geri Alındı"
                    elif t.get('status') == 'alindi':
                        t['status'] = 'yapildi'
                        t['completed_by'] = user_name or t.get('claimed_by', 'Ekip')
                        t['completed_at'] = datetime.now().strftime('%d.%m %H:%M')
                        t['updated_by'] = f"{user_name} (Tamamladı)" if user_name else "Tamamlandı"
                    else:
                        t['status'] = 'alindi'
                        t['claimed_by'] = user_name or 'Ekip Üyesi'
                        t['claimed_at'] = datetime.now().strftime('%d.%m %H:%M')
                        t['updated_by'] = f"{user_name} (Görevi Aldı)" if user_name else "Görevi Aldı"
                    found = True
                    break
            if found:
                save_ekip_data(data)
                self.send_json_response({'success': True, 'tasks': data.get('tasks', [])})
            else:
                self.send_json_response({'success': False, 'error': 'Görev bulunamadı'}, 404)
            return

        elif path == '/api/tasks/add':
            title = req_data.get('title', '').strip()
            if not title:
                self.send_json_response({'success': False, 'error': 'Görev başlığı gereklidir'}, 400)
                return

            new_task = {
                'id': f"tsk_{int(time.time() * 1000)}",
                'title': title,
                'description': req_data.get('description', '').strip(),
                'assignee': req_data.get('assignee', 'Genel Saha'),
                'category': req_data.get('category', 'Saha İçi Operasyon & Tamamlayıcı Lojistik'),
                'priority': req_data.get('priority', 'Orta'),
                'status': 'yapilacak',
                'deadline': req_data.get('deadline', datetime.now().strftime('%Y-%m-%d')),
                'claimed_by': '',
                'claimed_at': '',
                'completed_by': '',
                'completed_at': '',
                'updated_by': f"{req_data.get('user_name', 'Berke')} (Oluşturdu)"
            }
            data.setdefault('tasks', []).append(new_task)
            save_ekip_data(data)
            self.send_json_response({'success': True, 'tasks': data['tasks']})
            return

        elif path == '/api/tasks/delete':
            task_id = req_data.get('id')
            data['tasks'] = [t for t in data.get('tasks', []) if t.get('id') != task_id]
            save_ekip_data(data)
            self.send_json_response({'success': True, 'tasks': data['tasks']})
            return

        elif path == '/api/inventory/update':
            inv_id = req_data.get('id')
            current = req_data.get('current')
            status = req_data.get('status')
            found = False
            for item in data.get('inventory', []):
                if item['id'] == inv_id:
                    if current is not None:
                        item['current'] = int(current)
                    if status:
                        item['status'] = status
                        if status in ['Temin Edildi', 'temin_edildi', 'Hazır'] and item.get('current', 0) == 0:
                            item['current'] = item.get('target', 10)
                    if 'item' in req_data: item['item'] = req_data['item'].strip()
                    if 'category' in req_data: item['category'] = req_data['category'].strip()
                    if 'category_title' in req_data: item['category_title'] = req_data['category_title'].strip()
                    if 'target' in req_data: item['target'] = int(req_data['target'])
                    if 'unit' in req_data: item['unit'] = req_data['unit'].strip()
                    if 'source' in req_data: item['source'] = req_data['source'].strip()
                    if 'responsible' in req_data: item['responsible'] = req_data['responsible'].strip()
                    if 'notes' in req_data: item['notes'] = req_data['notes'].strip()
                    item['updated_by'] = req_data.get('user_name', 'Ekip')
                    item['updated_at'] = datetime.now().strftime('%d.%m.%Y %H:%M')
                    found = True
                    break
            if found:
                save_ekip_data(data)
                self.send_json_response({'success': True, 'inventory': data['inventory']})
            else:
                self.send_json_response({'success': False, 'error': 'Öğe bulunamadı'}, 404)
            return

        elif path == '/api/inventory/add':
            item_name = req_data.get('item', '').strip()
            if not item_name:
                self.send_json_response({'success': False, 'error': 'İçerik/kalem adı zorunludur'}, 400)
                return

            cat_val = req_data.get('category', 'chill_lounge')
            cat_titles = {
                'chill_lounge': 'Chill Lounge & Oturma',
                'atmosphere_decor': 'Atmosfer, Işık & Dekor',
                'games_experience': 'Festival Oyunları & Deneyim',
                'logistics_stage': 'Çadır, Stant & Sahne Altyapısı'
            }

            new_inv = {
                'id': f"cosm_{int(time.time() * 1000)}",
                'item': item_name,
                'category': cat_val,
                'category_title': req_data.get('category_title') or cat_titles.get(cat_val, 'Saha İçeriği'),
                'target': int(req_data.get('target', 10)),
                'current': int(req_data.get('current', 0)),
                'unit': req_data.get('unit', 'Adet').strip(),
                'source': req_data.get('source', 'Genel Tedarik').strip(),
                'responsible': req_data.get('responsible', 'Saha Ekibi').strip(),
                'status': req_data.get('status', 'Sürece Alındı'),
                'notes': req_data.get('notes', '').strip(),
                'updated_by': req_data.get('user_name', 'Berke'),
                'updated_at': datetime.now().strftime('%d.%m.%Y %H:%M')
            }
            data.setdefault('inventory', []).append(new_inv)
            save_ekip_data(data)
            self.send_json_response({'success': True, 'inventory': data['inventory']})
            return

        elif path == '/api/inventory/delete':
            inv_id = req_data.get('id')
            data['inventory'] = [i for i in data.get('inventory', []) if i.get('id') != inv_id]
            save_ekip_data(data)
            self.send_json_response({'success': True, 'inventory': data['inventory']})
            return

        elif path == '/api/announcements/add':
            title = req_data.get('title', '').strip()
            content = req_data.get('content', '').strip()
            if not title or not content:
                self.send_json_response({'success': False, 'error': 'Başlık ve içerik gereklidir'}, 400)
                return
            new_ann = {
                'id': f"ann_{int(time.time() * 1000)}",
                'title': title,
                'content': content,
                'date': req_data.get('date', datetime.now().strftime('%H:%M (Bugün)'))
            }
            data.setdefault('announcements', []).insert(0, new_ann)
            save_ekip_data(data)
            self.send_json_response({'success': True, 'announcements': data['announcements']})
            return

        elif path == '/api/announcements/delete':
            ann_id = req_data.get('id')
            data['announcements'] = [a for a in data.get('announcements', []) if a.get('id') != ann_id]
            save_ekip_data(data)
            self.send_json_response({'success': True, 'announcements': data['announcements']})
            return

        elif path == '/api/festival/update':
            data.setdefault('festival', {}).update(req_data)
            save_ekip_data(data)
            self.send_json_response({'success': True, 'festival': data['festival']})
            return

        elif path == '/api/schedule/add':
            day_title = req_data.get('day')
            item_data = req_data.get('item', {})
            for day in data.get('schedule', []):
                if day['day'] == day_title:
                    item_data['id'] = f"ev_{int(time.time() * 1000)}"
                    day['items'].append(item_data)
                    break
            save_ekip_data(data)
            self.send_json_response({'success': True, 'schedule': data['schedule']})
            return

        elif path == '/api/schedule/delete':
            day_title = req_data.get('day')
            item_id = req_data.get('id')
            item_title = req_data.get('title')
            for day in data.get('schedule', []):
                if day['day'] == day_title:
                    if item_id:
                        day['items'] = [it for it in day['items'] if it.get('id') != item_id]
                    elif item_title:
                        day['items'] = [it for it in day['items'] if it.get('title') != item_title]
                    break
            save_ekip_data(data)
            self.send_json_response({'success': True, 'schedule': data['schedule']})
            return

        elif path == '/api/contacts/add':
            name = req_data.get('name', '').strip()
            phone = req_data.get('phone', '').strip()
            if not name or not phone:
                self.send_json_response({'success': False, 'error': 'İsim ve telefon zorunludur'}, 400)
                return
            new_cnt = {
                'id': f"cnt_{int(time.time() * 1000)}",
                'name': name,
                'role': req_data.get('role', 'Saha İletişim').strip(),
                'phone': phone,
                'internal': req_data.get('internal', '').strip()
            }
            data.setdefault('contacts', []).append(new_cnt)
            save_ekip_data(data)
            self.send_json_response({'success': True, 'contacts': data['contacts']})
            return

        elif path == '/api/contacts/delete':
            cnt_id = req_data.get('id')
            phone = req_data.get('phone')
            if cnt_id:
                data['contacts'] = [c for c in data.get('contacts', []) if c.get('id') != cnt_id]
            elif phone:
                data['contacts'] = [c for c in data.get('contacts', []) if c.get('phone') != phone]
            save_ekip_data(data)
            self.send_json_response({'success': True, 'contacts': data['contacts']})
            return

        elif path == '/api/partners/update':
            partner_id = req_data.get('id')
            found = False
            for p in data.get('partners', []):
                if p['id'] == partner_id:
                    for key in ['name', 'category', 'category_title', 'potential_offering',
                                'contact_person', 'email', 'phone', 'location_type',
                                'status', 'status_title', 'notes', 'mail_sent',
                                'mail_sent_date', 'mail_sent_by', 'mail_sent_subject']:
                        if key in req_data:
                            p[key] = req_data[key]
                    p['updated_by'] = req_data.get('user_name', 'Berke')
                    p['updated_at'] = datetime.now().strftime('%d.%m.%Y %H:%M')
                    found = True
                    break
            if found:
                save_ekip_data(data)
                self.send_json_response({'success': True, 'partners': data['partners']})
            else:
                self.send_json_response({'success': False, 'error': 'Partner bulunamadı'}, 404)
            return

        elif path == '/api/partners/add':
            name = req_data.get('name', '').strip()
            if not name:
                self.send_json_response({'success': False, 'error': 'Kurum / Firma adı zorunludur'}, 400)
                return

            new_partner = {
                'id': f"part_{int(time.time() * 1000)}",
                'name': name,
                'category': req_data.get('category', 'coffee_food'),
                'category_title': req_data.get('category_title', 'Kahve, Gıda & Stant'),
                'potential_offering': req_data.get('potential_offering', 'Stant & İkram'),
                'contact_person': req_data.get('contact_person', 'Yetkili'),
                'email': req_data.get('email', '').strip(),
                'phone': req_data.get('phone', '').strip(),
                'location_type': req_data.get('location_type', 'Yerel İşletme / Süleymanpaşa'),
                'status': req_data.get('status', 'in_progress'),
                'status_title': req_data.get('status_title', 'Görüşülüyor'),
                'notes': req_data.get('notes', '').strip(),
                'mail_sent': bool(req_data.get('mail_sent', False)),
                'mail_sent_date': req_data.get('mail_sent_date', ''),
                'mail_sent_by': req_data.get('mail_sent_by', ''),
                'mail_sent_subject': req_data.get('mail_sent_subject', ''),
                'created_by': req_data.get('user_name', 'Berke'),
                'updated_at': datetime.now().strftime('%d.%m.%Y %H:%M')
            }
            data.setdefault('partners', []).append(new_partner)
            save_ekip_data(data)
            self.send_json_response({'success': True, 'partners': data['partners']})
            return

        elif path == '/api/partners/delete':
            partner_id = req_data.get('id')
            data['partners'] = [p for p in data.get('partners', []) if p.get('id') != partner_id]
            save_ekip_data(data)
            self.send_json_response({'success': True, 'partners': data['partners']})
            return

        self.send_json_response({'error': 'Gecersiz Endpoint'}, 404)

def keep_alive_worker():
    """Render.com free tier uyku moduna geçmesin diye 10 dakikada bir kendini uyarır."""
    time.sleep(30)
    ext_url = os.environ.get('RENDER_EXTERNAL_URL', '')
    while True:
        try:
            target = f"{ext_url}/health" if ext_url else f"http://127.0.0.1:{PORT}/health"
            req = urllib.request.Request(target, headers={'User-Agent': 'SET-KeepAlive/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
        except Exception:
            pass
        time.sleep(600) # 10 dakika

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SetUnifiedHandler)
    url = f"http://0.0.0.0:{PORT}"

    print(f"\n=======================================================")
    print(f"  SET KAMPÜSE HOŞ GELDİN FEST — 7/24 BULUT SUNUCUSU")
    print(f"  Port: {PORT}")
    print(f"  Ekip Paneli:   {url}/")
    print(f"  Kroki Paneli:  {url}/kroki/")
    print(f"=======================================================\n")

    t = threading.Thread(target=keep_alive_worker, daemon=True)
    t.start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nBulut sunucusu durduruldu.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
