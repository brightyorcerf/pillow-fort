CREATE TABLE users (
	id UUID NOT NULL, 
	email VARCHAR(320) NOT NULL, 
	hashed_password TEXT, 
	username VARCHAR(64) NOT NULL, 
	roles VARCHAR[] DEFAULT '{player}' NOT NULL, 
	is_email_verified BOOLEAN NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	failed_login_attempts INTEGER NOT NULL, 
	locked_until TIMESTAMP WITH TIME ZONE, 
	oauth_provider VARCHAR(32), 
	oauth_provider_id VARCHAR(256), 
	email_verification_token VARCHAR(256), 
	password_reset_token VARCHAR(256), 
	password_reset_expires TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_users_oauth ON users (oauth_provider, oauth_provider_id);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE TABLE characters (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	hp INTEGER NOT NULL, 
	current_streak INTEGER NOT NULL, 
	longest_streak INTEGER NOT NULL, 
	total_study_minutes INTEGER NOT NULL, 
	life_shields INTEGER NOT NULL, 
	rituals_used INTEGER NOT NULL, 
	ghosting_days INTEGER NOT NULL, 
	has_flow_state_buff BOOLEAN NOT NULL, 
	is_permanently_dead BOOLEAN NOT NULL, 
	is_in_penance BOOLEAN NOT NULL, 
	weekly_consistency_multiplier FLOAT NOT NULL, 
	consecutive_below_average_days INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_characters_user_id ON characters (user_id);
CREATE TABLE hp_logs (
	id UUID NOT NULL, 
	character_id UUID NOT NULL, 
	old_hp INTEGER NOT NULL, 
	new_hp INTEGER NOT NULL, 
	delta INTEGER NOT NULL, 
	reason VARCHAR(64) NOT NULL, 
	description TEXT NOT NULL, 
	shield_used BOOLEAN NOT NULL, 
	triggered_death BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_hp_logs_reason ON hp_logs (reason);
CREATE INDEX ix_hp_logs_character_id ON hp_logs (character_id);
CREATE INDEX ix_hp_logs_created_at ON hp_logs (created_at);
CREATE TABLE death_records (
	id UUID NOT NULL, 
	character_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	cause VARCHAR(64) NOT NULL, 
	hp_at_death INTEGER NOT NULL, 
	total_hours_in_life FLOAT NOT NULL, 
	consecutive_ghost_days_at_death INTEGER NOT NULL, 
	rituals_used_at_death INTEGER NOT NULL, 
	longest_streak_at_death INTEGER NOT NULL, 
	eulogy_generated BOOLEAN NOT NULL, 
	is_permanent BOOLEAN NOT NULL, 
	promises_id UUID, 
	died_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_death_records_character_id ON death_records (character_id);
CREATE INDEX ix_death_records_user_id ON death_records (user_id);
CREATE TABLE revival_attempts (
	id UUID NOT NULL, 
	character_id UUID NOT NULL, 
	death_record_id UUID NOT NULL, 
	method VARCHAR(64) NOT NULL, 
	hp_restored_to INTEGER NOT NULL, 
	success BOOLEAN NOT NULL, 
	fail_reason TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_revival_attempts_death_record_id ON revival_attempts (death_record_id);
CREATE INDEX ix_revival_attempts_character_id ON revival_attempts (character_id);
CREATE TABLE penance_streaks (
	id UUID NOT NULL, 
	character_id UUID NOT NULL, 
	death_record_id UUID NOT NULL, 
	attempt_number INTEGER NOT NULL, 
	required_days INTEGER NOT NULL, 
	days_completed INTEGER NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	started_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	failed_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_penance_streaks_character_id ON penance_streaks (character_id);
CREATE TABLE phoenix_feathers (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	character_id UUID, 
	status VARCHAR(32) NOT NULL, 
	price_paid_stardust INTEGER NOT NULL, 
	acquired_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	used_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_phoenix_feathers_user_id ON phoenix_feathers (user_id);
CREATE TABLE eulogies (
	id UUID NOT NULL, 
	character_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	death_record_id UUID NOT NULL, 
	character_name VARCHAR(64) NOT NULL, 
	total_study_hours FLOAT NOT NULL, 
	longest_streak INTEGER NOT NULL, 
	rank_achieved VARCHAR(32) NOT NULL, 
	life_shields_earned INTEGER NOT NULL, 
	rituals_completed INTEGER NOT NULL, 
	total_covenants_signed INTEGER NOT NULL, 
	total_covenants_kept INTEGER NOT NULL, 
	born_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	died_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (death_record_id)
);
CREATE INDEX ix_eulogies_user_id ON eulogies (user_id);
CREATE INDEX ix_eulogies_character_id ON eulogies (character_id);
CREATE TABLE wallets (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	coin_balance INTEGER NOT NULL, 
	total_coins_earned INTEGER NOT NULL, 
	total_coins_spent INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_wallets_user_id ON wallets (user_id);
CREATE TABLE vault_wallets (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	star_dust_balance INTEGER NOT NULL, 
	total_star_dust_purchased INTEGER NOT NULL, 
	total_star_dust_spent INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_vault_wallets_user_id ON vault_wallets (user_id);
CREATE TABLE vault_ledger (
	id UUID NOT NULL, 
	vault_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	delta INTEGER NOT NULL, 
	reason VARCHAR(32) NOT NULL, 
	description VARCHAR(256) NOT NULL, 
	balance_after INTEGER NOT NULL, 
	reference_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_vault_ledger_user_id ON vault_ledger (user_id);
CREATE INDEX ix_vault_ledger_vault_id ON vault_ledger (vault_id);
CREATE TABLE store_items (
	id UUID NOT NULL, 
	name VARCHAR(128) NOT NULL, 
	description VARCHAR(512) NOT NULL, 
	item_type VARCHAR(32) NOT NULL, 
	category VARCHAR(32) NOT NULL, 
	price_currency VARCHAR(16) NOT NULL, 
	price_amount INTEGER NOT NULL, 
	discounted_amount INTEGER, 
	required_level INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	max_per_user INTEGER, 
	image_url VARCHAR(512), 
	metadata_json TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE INDEX ix_store_items_item_type ON store_items (item_type);
CREATE INDEX ix_store_items_category ON store_items (category);
CREATE TABLE special_offers (
	id UUID NOT NULL, 
	title VARCHAR(128) NOT NULL, 
	description VARCHAR(512) NOT NULL, 
	bundled_item_ids_json TEXT NOT NULL, 
	bundle_currency VARCHAR(16) NOT NULL, 
	bundle_price INTEGER NOT NULL, 
	original_total INTEGER NOT NULL, 
	required_level INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE, 
	image_url VARCHAR(512), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE transactions (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	item_id UUID, 
	offer_id UUID, 
	item_name VARCHAR(128) NOT NULL, 
	currency VARCHAR(16) NOT NULL, 
	amount_paid INTEGER NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	fail_reason VARCHAR(256), 
	refunded_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_transactions_item_id ON transactions (item_id);
CREATE INDEX ix_transactions_user_id ON transactions (user_id);
CREATE INDEX ix_transactions_status ON transactions (status);
CREATE TABLE owned_items (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	item_id UUID NOT NULL, 
	item_name VARCHAR(128) NOT NULL, 
	item_type VARCHAR(32) NOT NULL, 
	quantity INTEGER NOT NULL, 
	is_consumable BOOLEAN NOT NULL, 
	is_equipped BOOLEAN NOT NULL, 
	acquired_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_owned_items_user_id ON owned_items (user_id);
CREATE INDEX ix_owned_items_item_id ON owned_items (item_id);
CREATE TABLE refresh_tokens (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	token_hash VARCHAR(256) NOT NULL, 
	device_fingerprint VARCHAR(256), 
	ip_address VARCHAR(45), 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	is_revoked BOOLEAN NOT NULL, 
	replaced_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_refresh_tokens_user_active ON refresh_tokens (user_id, is_revoked);
CREATE UNIQUE INDEX ix_refresh_tokens_token_hash ON refresh_tokens (token_hash);
CREATE TABLE covenants (
	id UUID NOT NULL, 
	character_id UUID NOT NULL, 
	covenant_date DATE NOT NULL, 
	subject_type VARCHAR(32) NOT NULL, 
	goal_minutes INTEGER NOT NULL, 
	actual_minutes INTEGER NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	is_signed BOOLEAN NOT NULL, 
	signed_at TIMESTAMP WITH TIME ZONE, 
	hp_gain_multiplier FLOAT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_covenants_char_date ON covenants (character_id, covenant_date);
CREATE TABLE study_sessions (
	id UUID NOT NULL, 
	character_id UUID NOT NULL, 
	covenant_id UUID NOT NULL, 
	started_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	ended_at TIMESTAMP WITH TIME ZONE, 
	duration_minutes INTEGER NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	check_in_count INTEGER NOT NULL, 
	check_in_passed INTEGER NOT NULL, 
	was_foreground BOOLEAN NOT NULL, 
	idle_violations INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE, 
	FOREIGN KEY(covenant_id) REFERENCES covenants (id) ON DELETE CASCADE
);
CREATE INDEX ix_sessions_char_status ON study_sessions (character_id, status);
