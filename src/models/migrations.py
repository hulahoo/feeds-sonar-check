from loguru import logger

from src.models.base import SyncPostgresDriver


def create_migrations():
    with SyncPostgresDriver().session() as db:
        logger.info("Start executing migrations...")

        # create enums
        db.execute(
            "create type update_status_enum as enum ('ENABLED', 'DISABLED', 'UPDATE_ERROR');")
        db.execute("create type auth_type as enum ('NAU', 'API', 'BSC')")
        db.execute(
            "create type format_of_feed as enum ('CSV', 'JSON', 'XML', 'TXT')")
        db.execute(
            "create type types as enum ('FEMA', 'SEMA', 'MD5H', 'SHA1', 'SHA2', 'IPAD', 'URLS', 'DOMN', 'FILE', 'REGS')")
        db.execute(
            "create type format as enum ('STIX', 'MISP', 'FREE_TEXT', 'JSON', 'CSV')")

        # create tag
        db.execute('create table "tag" ("id" serial not null primary key, "name" varchar(30), "created_at" timestamp not null, "colour" varchar(30), "exportable" boolean);')

        # create statistic
        db.execute(
            'create table "statistic" ("id" serial not null primary key, "created_at" timestamp not null, "data" jsonb default null);')

        # create indicator
        db.execute('CREATE TABLE "indicator" ("id" SERIAL NOT NULL PRIMARY KEY, "uuid" VARCHAR(255), "category" VARCHAR(128) NOT NULL, "ttl" TIMESTAMP NOT NULL, "comment" TEXT DEFAULT NULL, "is_archived" BOOLEAN, "false_or_positive" BOOLEAN DEFAULT false, "push_to_detections" BOOLEAN DEFAULT false, "enrichment_context" JSONB DEFAULT NULL, "created_at" timestamp NOT NULL, "type" types NOT NULL, "value" varchar(256) NOT NULL, "updated_date" timestamp NOT NULL, "weight" integer NOT NULL, "false_detected" integer NOT NULL, "positive_detected" integer NOT NULL, "detected" integer NOT NULL, "first_detected_date" timestamp NULL, "last_detected_date" timestamp NULL, "supplier_name" varchar(128) NOT NULL, "supplier_vendor_name" varchar(128) NOT NULL, "supplier_type" varchar(64) NOT NULL, "supplier_confidence" integer NOT NULL, "supplier_created_date" timestamp NULL, "ioc_context_exploits_md5" varchar(64) NULL, "ioc_context_exploits_sha1" varchar(64) NULL, "ioc_context_exploits_sha256" varchar(64) NULL, "ioc_context_exploits_threat" varchar(64) NULL, "ioc_context_av_verdict" varchar(64) NULL, "ioc_context_md5" varchar(64) NULL, "ioc_context_sha1" varchar(64) NULL, "ioc_context_sha256" varchar(64) NULL, "ioc_context_affected_products_product" varchar(64) NULL, "joc_context_domains" varchar(64) NULL, "ioc_context_file_names" varchar(64) NULL, "ioc_context_file_size" varchar(64) NULL, "ioc_context_file_type" varchar(64) NULL, "ioc_context_files_behaviour" varchar(64) NULL, "ioc_context_files_md5" varchar(64) NULL, "ioc_context_files_sha1" varchar(64) NULL, "ioc_context_files_sha256" varchar(64) NULL, "ioc_context_files_threat" varchar(64) NULL, "ioc_context_malware" varchar(64) NULL, "ioc_context_mask" varchar(64) NULL, "ioc_context_popularity" varchar(64) NULL, "ioc_context_port" varchar(64) NULL, "ioc_context_protocol" varchar(64) NULL, "ioc_context_publication_name" varchar(64) NULL, "ioc_context_severity" varchar(64) NULL, "ioc_context_type" varchar(64) NULL, "ioc_context_url" varchar(64) NULL, "ioc_context_urls_url" varchar(64) NULL, "ioc_context_vendors_vendor" varchar(64) NULL, "ioc_context_geo" varchar(64) NULL, "ioc_context_id" varchar(64) NULL, "ioc_context_industry" varchar(64) NULL, "ioc_context_ip" varchar(64) NULL, "ioc_context_ip_geo" varchar(64) NULL, "ioc_context_ip_whois_asn" varchar(64) NULL, "ioc_context_ip_whois_contact_abuse_country" varchar(64) NULL, "ioc_context_ip_whois_contact_abuse_email" varchar(64) NULL, "ioc_context_ip_whois_contact_abuse_name" varchar(64) NULL, "ioc_context_ip_whois_contact_owner_city" varchar(64) NULL, "ioc_context_ip_whois_contact_owner_code" varchar(64) NULL, "ioc_context_ip_whois_contact_owner_country" varchar(64) NULL, "ioc_context_ip_whois_contact_owner_email" varchar(64) NULL, "ioc_context_ip_whois_contact_owner_name" varchar(64) NULL, "ioc_context_ip_whois_country" varchar(64) NULL, "ioc_context_ip_whois_created" varchar(64) NULL, "ioc_context_ip_whois_desrc" varchar(64) NULL, "ioc_context_ip_whois_net_name" varchar(64) NULL, "ioc_context_ip_whois_net_range" varchar(64) NULL, "ioc_context_ip_whois_updated" varchar(64) NULL, "ioc_context_whois_mx" varchar(64) NULL, "ioc_context_whois_mx_ips" varchar(64) NULL, "ioc_context_whois_ns" varchar(64) NULL, "ioc_context_whois_ns_ips" varchar(64) NULL, "ioc_context_whois_city" varchar(64) NULL, "ioc_context_whois_country" varchar(64) NULL, "ioc_context_whois_created" varchar(64) NULL, "ioc_context_whois_domain" varchar(64) NULL, "ioc_context_whois_email" varchar(64) NULL, "ioc_context_whois_expires" varchar(64) NULL, "ioc_context_whois_name" varchar(64) NULL, "ioc_context_whois_org" varchar(64) NULL, "ioc_context_whois_registrar_email" varchar(64) NULL, "ioc_context_whois_registrar_name" varchar(64) NULL, "ioc_context_whois_updated" varchar(64) NULL);')
        db.execute('CREATE TABLE "indicator_tag_m2m_table" ("id" SERIAL NOT NULL PRIMARY KEY, "indicator_id" bigint NOT NULL REFERENCES "indicator" ("id") DEFERRABLE INITIALLY DEFERRED, "tag_id" bigint NOT NULL REFERENCES "tag" ("id") DEFERRABLE INITIALLY DEFERRED);')
        db.execute('CREATE UNIQUE INDEX "intelhandler_indicator_tag_indicator_id_tag_id_8fc7aa63_uniq" ON "indicator_tag_m2m_table" ("indicator_id", "tag_id");')
        db.execute(
            'CREATE INDEX "intelhandler_indicator_tag_indicator_id_1dad0ba7" ON "indicator_tag_m2m_table" ("indicator_id");')
        db.execute(
            'CREATE INDEX "intelhandler_indicator_tag_tag_id_2033539f" ON "indicator_tag_m2m_table" ("tag_id");')
        db.execute(
            'CREATE INDEX "intelhandler_is_archived_attribute_mispobject_id_37232155" ON "indicator" ("is_archived");')

        # create parsing_rule
        db.execute(
            'create table "parsing_rule" ("id" serial not null primary key,  "created_at" timestamp not null);')

        # create source
        db.execute('create table "source" ("id" serial not null primary key,  "created_at" timestamp not null, "is_instead_full" boolean default false, "is_active" boolean default true, "provider_name" varchar(255) not null, "path" text not null, "certificate_file_name" varchar(50), certificate bytea, "authenticity" integer default 0, "records_quantity" integer, "format" format, "auth_type" auth_type, "auth_login" varchar(32), "auth_password" varchar(64), "max_rows" int default 0, "raw_indicators" text default null, "update_time_period" integer default 0);')

        # create feed
        db.execute('CREATE TABLE "feed" ("id" SERIAL NOT NULL PRIMARY KEY, "ts" timestamp NOT NULL, "sertificate_file_name" VARCHAR(50), "custom_field" VARCHAR(120), "source" INTEGER REFERENCES source (id), "update_status" update_status_enum, "created_at" timestamp NOT NULL, "modified" timestamp NOT NULL, "type_of_feed" types NOT NULL, "format_of_feed" format_of_feed NOT NULL, "auth_type" auth_type NOT NULL, "polling_frequency" varchar(3) NOT NULL, "auth_login" varchar(32) NULL, "auth_password" varchar(64) NULL, "ayth_querystring" varchar(128) NULL, "separator" varchar(8) NULL, "sertificate" varchar(100) NULL, "vendor" varchar(32) NOT NULL, "name" varchar(32) NOT NULL UNIQUE, "link" varchar(100) NOT NULL, "confidence" integer NOT NULL, "records_quantity" integer NULL);')
        # create feed_indicator_m2m_table
        db.execute('create table "feed_indicator_m2m_table" ("id" serial not null primary key, "feed_id" bigint not null references "feed" ("id") deferrable initially deferred, "indicator_id" bigint references "indicator" ("id") DEFERRABLE INITIALLY DEFERRED);')
        db.execute(
            'CREATE UNIQUE INDEX "feed_indicator_m2m_table_41251221" ON "feed_indicator_m2m_table" ("indicator_id", "feed_id");')
        # create feed_parsing_rule_m2m_table
        db.execute('create table "feed_parsing_rule_m2m_table" ("id" serial not null primary key, "parsing_rule_id" bigint references "parsing_rule" ("id") deferrable initially deferred, "feed_id" bigint references "feed" ("id") DEFERRABLE INITIALLY DEFERRED );')

        db.flush()
        db.commit()
