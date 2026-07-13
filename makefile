update_qdm:
	qmd update
	qmd embed

TP_SHARE_DEST ?= /Volumes/tp-share/backend-knowledge

define rsync_vault_subset
	rsync -av --prune-empty-dirs \
		--include='*/' \
		--include='*.md' \
		--include='.obsidian/***' \
		--exclude='*' \
		./ $(1)/
endef

sync_tp_share:
	$(call rsync_vault_subset,$(TP_SHARE_DEST))
