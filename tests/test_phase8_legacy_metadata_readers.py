import json
import sqlite3
from pathlib import Path

from app.legacy_metadata import canonical_db_metadata, canonical_metadata_available, resolve_legacy_metadata
from app.metadata_schema import apply_video_schema_migrations


def make_db(tmp_path: Path):
    db=tmp_path/'library.db'
    con=sqlite3.connect(db)
    con.execute('''CREATE TABLE videos(
      video_id TEXT PRIMARY KEY,url TEXT,original_title TEXT,clean_title TEXT,channel TEXT,upload_date TEXT,
      description TEXT,local_folder TEXT,youtube_category_name TEXT,youtube_tags TEXT,metadata_schema_version INTEGER DEFAULT 0,
      metadata_migration_status TEXT
    )''')
    apply_video_schema_migrations(con);con.commit()
    return db,con


def make_folder(tmp_path, vid='abcdefghijk', with_info=True):
    folder=tmp_path/'downloads'/'Category'/'Channel'/f'2020-01-02 - Example'
    data=folder/'_data';data.mkdir(parents=True)
    (data/'.video_id').write_text(vid,encoding='utf-8')
    if with_info:
        info={"id":vid,"title":"Info title","channel":"Info channel","upload_date":"20200103","webpage_url":f"https://youtube.com/watch?v={vid}","description":"Info desc","categories":["Info category"]}
        (data/f'{vid}.info.json').write_text(json.dumps(info),encoding='utf-8')
    return folder


def test_canonical_resolver_prefers_sqlite_over_info_json(tmp_path):
    _,con=make_db(tmp_path);folder=make_folder(tmp_path)
    con.execute("INSERT INTO videos(video_id,url,original_title,channel,upload_date,description,local_folder,youtube_category_name,metadata_schema_version) VALUES(?,?,?,?,?,?,?,?,1)",('abcdefghijk','db-url','DB title','DB channel','2020-01-02','DB desc',str(folder),'DB category'))
    con.commit()
    out=resolve_legacy_metadata(con,'abcdefghijk',folder)
    assert out['original_title']=='DB title'
    assert out['channel']=='DB channel'
    assert out['upload_date']=='2020-01-02'
    assert out['youtube_category_name']=='DB category'
    assert out['_sources']==['sqlite','info_json_fallback']
    con.close()


def test_resolver_falls_back_to_info_json_for_blank_db_fields(tmp_path):
    _,con=make_db(tmp_path);folder=make_folder(tmp_path)
    con.execute("INSERT INTO videos(video_id,local_folder) VALUES(?,?)",('abcdefghijk',str(folder)));con.commit()
    out=resolve_legacy_metadata(con,'abcdefghijk',folder)
    assert out['original_title']=='Info title'
    assert out['channel']=='Info channel'
    assert out['upload_date']=='2020-01-03'
    assert out['youtube_category_name']=='Info category'
    con.close()


def test_canonical_metadata_available_for_migrated_row(tmp_path):
    _,con=make_db(tmp_path);folder=make_folder(tmp_path,with_info=False)
    con.execute("INSERT INTO videos(video_id,original_title,channel,metadata_schema_version,local_folder) VALUES(?,?,?,?,?)",('abcdefghijk','DB title','DB channel',1,str(folder)));con.commit()
    assert canonical_metadata_available(con,'abcdefghijk') is True
    con.close()


def test_local_artifact_missing_list_does_not_require_info_json_when_canonical_exists(tmp_path,monkeypatch):
    from app import app
    db,con=make_db(tmp_path);folder=make_folder(tmp_path,with_info=False);data=folder/'_data'
    con.execute("INSERT INTO videos(video_id,original_title,channel,metadata_schema_version,local_folder) VALUES(?,?,?,?,?)",('abcdefghijk','DB title','DB channel',1,str(folder)));con.commit();con.close()
    (folder/'video.mp4').write_bytes(b'x')
    (data/'x.srt').write_text('x',encoding='utf-8')
    (data/'x.transcript.txt').write_text('x',encoding='utf-8')
    (data/'x.description').write_text('x',encoding='utf-8')
    (data/'x.jpg').write_bytes(b'x')
    monkeypatch.setattr(app,'DB',db);monkeypatch.setattr(app,'locate_existing_folder',lambda vid: folder)
    missing=app.local_artifact_missing_list('abcdefghijk')
    assert 'Info JSON' not in missing and 'Metadata' not in missing


def test_artifact_inventory_marks_canonical_metadata_without_info_json(tmp_path,monkeypatch):
    from app import app
    db,con=make_db(tmp_path);folder=make_folder(tmp_path,with_info=False)
    con.execute("INSERT INTO videos(video_id,original_title,channel,metadata_schema_version,local_folder) VALUES(?,?,?,?,?)",('abcdefghijk','DB title','DB channel',1,str(folder)));con.commit();con.close()
    monkeypatch.setattr(app,'DB',db)
    inv=app.artifact_inventory('abcdefghijk',folder)
    assert inv['info_json'] is None
    assert inv['canonical_metadata'] is True
    assert inv['metadata_source']=='sqlite'


def test_transcript_archive_complete_without_info_json_when_canonical_exists(tmp_path,monkeypatch):
    from app import app
    db,con=make_db(tmp_path);folder=make_folder(tmp_path,with_info=False);data=folder/'_data'
    con.execute("INSERT INTO videos(video_id,original_title,channel,metadata_schema_version,local_folder) VALUES(?,?,?,?,?)",('abcdefghijk','DB title','DB channel',1,str(folder)));con.commit();con.close()
    (folder/'video.mp4').write_bytes(b'x')
    (data/'x.srt').write_text('x',encoding='utf-8')
    (data/'abcdefghijk.transcript.txt').write_text('x',encoding='utf-8')
    (data/'x.description').write_text('x',encoding='utf-8')
    (data/'x.jpg').write_bytes(b'x')
    monkeypatch.setattr(app,'DB',db);monkeypatch.setattr(app,'locate_existing_folder',lambda vid: folder)
    category,status=app.transcript_archive_category('abcdefghijk')
    assert category=='complete'
    assert status['metadata'] is True and status['info_json'] is False and status['canonical_metadata'] is True


def test_resolve_folder_metadata_prefers_canonical_db(tmp_path,monkeypatch):
    from app import app
    db,con=make_db(tmp_path);folder=make_folder(tmp_path,with_info=True)
    con.execute("INSERT INTO videos(video_id,channel,upload_date,metadata_schema_version,local_folder) VALUES(?,?,?,?,?)",('abcdefghijk','DB channel','2020-01-02',1,str(folder)));con.commit();con.close()
    monkeypatch.setattr(app,'DB',db);monkeypatch.setattr(app,'_read_csv_metadata_for_video',lambda vid:{})
    assert app.resolve_folder_metadata('abcdefghijk',folder)==('DB channel','2020-01-02')


def test_one_click_folder_record_uses_canonical_db_before_info_json(tmp_path,monkeypatch):
    from app import app
    db,con=make_db(tmp_path);folder=make_folder(tmp_path,with_info=True);data=folder/'_data'
    (folder/'video.mp4').write_bytes(b'x')
    (data/'x.original-title').write_text('Marker title',encoding='utf-8')
    con.execute("INSERT INTO videos(video_id,url,original_title,clean_title,channel,upload_date,description,metadata_schema_version,local_folder) VALUES(?,?,?,?,?,?,?,?,?)",('abcdefghijk','db-url','DB title','DB clean','DB channel','2020-01-02','DB desc',1,str(folder)));con.commit();con.close()
    monkeypatch.setattr(app,'DB',db)
    rec=app.one_click_folder_record(data/'.video_id')
    assert rec['url']=='db-url'
    assert rec['original_title']=='Marker title'  # original-title marker remains presentation source when present
    assert rec['clean_title']=='DB title'
    assert rec['channel']=='DB channel'
    assert rec['upload_date']=='2020-01-02'
    assert rec['description']=='DB desc'

def test_validate_video_outputs_accepts_canonical_metadata_without_info_json(tmp_path,monkeypatch):
    from app import app
    db,con=make_db(tmp_path);folder=make_folder(tmp_path,with_info=False);data=folder/'_data'
    con.execute("INSERT INTO videos(video_id,original_title,channel,metadata_schema_version,local_folder) VALUES(?,?,?,?,?)",('abcdefghijk','DB title','DB channel',1,str(folder)));con.commit();con.close()
    video=folder/'video.mp4';video.write_bytes(b'x')
    (folder/'x.original-title').write_text('DB title',encoding='utf-8')
    (data/'abcdefghijk.transcript.txt').write_text('[00:00] text',encoding='utf-8')
    (data/'x.transcript_detailed.json').write_text('{}',encoding='utf-8')
    (data/'x.description').write_text('desc',encoding='utf-8')
    (data/'x.jpg').write_bytes(b'x')
    report=folder/'x.report.html'
    report.write_text(f'''<html><select id="speedSelect"></select><h3>Detailed Summary</h3><details><summary><b>Source Transcript</b></summary><div class="source-range"></div></details><script>seekTo(1)</script>VideoLibraryManager v{app.APP_VERSION}</html>''',encoding='utf-8')
    monkeypatch.setattr(app,'DB',db)
    ok,checks=app.validate_video_outputs(folder,'x','abcdefghijk',video,report,False)
    assert ok is True
    names={n:passed for n,passed,_ in checks}
    assert names['Metadata'] is True
    assert 'Info JSON' not in names


def test_phase1_rebuild_db_from_folders_prefers_canonical_db(tmp_path,monkeypatch):
    from app import app
    db,con=make_db(tmp_path)
    downloads=tmp_path/'downloads';folder=downloads/'Category'/'Channel'/'2020-01-02 - Example';data=folder/'_data';data.mkdir(parents=True)
    (data/'.video_id').write_text('abcdefghijk',encoding='utf-8')
    (folder/'video.mp4').write_bytes(b'x')
    # conflicting retained info.json should lose to canonical DB
    (data/'abcdefghijk.info.json').write_text(json.dumps({'id':'abcdefghijk','title':'Info title','channel':'Info channel','upload_date':'20200103','webpage_url':'info-url','description':'Info desc'}),encoding='utf-8')
    con.execute("INSERT INTO videos(video_id,url,original_title,clean_title,channel,upload_date,description,local_folder,metadata_schema_version) VALUES(?,?,?,?,?,?,?,?,1)",('abcdefghijk','db-url','DB title','DB clean','DB channel','2020-01-02','DB desc',str(folder)));con.commit();con.close()
    monkeypatch.setattr(app,'DB',db);monkeypatch.setattr(app,'BASE',tmp_path);monkeypatch.setattr(app,'DOWNLOADS',downloads)
    rebuilt=app.phase1_rebuild_db_from_folders()
    rcon=sqlite3.connect(rebuilt)
    row=rcon.execute('SELECT url,original_title,channel,upload_date,description FROM videos WHERE video_id=?',('abcdefghijk',)).fetchone();rcon.close()
    assert row==('db-url','DB title','DB channel','2020-01-02','DB desc')
