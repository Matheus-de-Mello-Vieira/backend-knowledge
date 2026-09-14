-include .env

FTP_HOST ?= 
FTP_PORT ?= 21
FTP_USER ?=
FTP_PASSWORD ?=
FTP_DEST ?= /G/backend-knowledge

define upload_vault_subset
	@staging_dir="$$(mktemp -d)"; \
	trap 'rm -rf "$$staging_dir"' EXIT; \
	rsync -a --prune-empty-dirs \
		--include='.obsidian/' \
		--include='.obsidian/***' \
		--exclude='.*' \
		--include='*/' \
		--include='*.md' \
		--exclude='*' \
		./ "$$staging_dir/"; \
	lftp \
		-u "$(FTP_USER),$(FTP_PASSWORD)" \
		-p "$(FTP_PORT)" \
		"$(FTP_HOST)" \
		-e "set cmd:fail-exit yes; \
		    mkdir -p -f \"$(FTP_DEST)\"; \
		    mirror \
		        --reverse \
		        --verbose \
		        --delete \
				--no-perms \
		        --parallel=4 \
		        \"$$staging_dir\" \
		        \"$(FTP_DEST)\"; \
		    bye"
endef

.PHONY: upload_vault_ftp
upload_vault_ftp:
	$(call upload_vault_subset)

.PHONY: update_qdm
update_qdm:
	qmd update
	qmd cleanup
	QMD_LLAMA_GPU=metal qmd embed