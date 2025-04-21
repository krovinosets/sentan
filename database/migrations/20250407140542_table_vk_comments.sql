-- +goose Up
-- +goose StatementBegin
BEGIN;

CREATE TABLE vk_comments (
    id SERIAL PRIMARY KEY,
    comment_id INTEGER UNIQUE NOT NULL,
    text TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    date TIMESTAMP NOT NULL
);

CREATE INDEX idx_author_id ON vk_comments(author_id);
CREATE INDEX idx_date ON vk_comments(date);

COMMIT;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS vk_comments;
-- +goose StatementEnd


