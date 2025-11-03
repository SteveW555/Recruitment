-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "email" TEXT NOT NULL,
    "name" TEXT,
    "gmailAddress" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL,
    "lastLoginAt" DATETIME
);

-- CreateTable
CREATE TABLE "user_tokens" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT NOT NULL,
    "accessToken" TEXT NOT NULL,
    "refreshToken" TEXT NOT NULL,
    "tokenExpiry" DATETIME NOT NULL,
    "scopes" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL,
    CONSTRAINT "user_tokens_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "downloaded_files" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT NOT NULL,
    "emailId" TEXT NOT NULL,
    "attachmentId" TEXT NOT NULL,
    "filename" TEXT NOT NULL,
    "mimeType" TEXT NOT NULL,
    "size" INTEGER NOT NULL,
    "localPath" TEXT NOT NULL,
    "downloadedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expiresAt" DATETIME NOT NULL,
    "deletedAt" DATETIME,
    CONSTRAINT "downloaded_files_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "search_queries" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT NOT NULL,
    "startDate" DATETIME NOT NULL,
    "endDate" DATETIME NOT NULL,
    "senderFilter" TEXT,
    "subjectFilter" TEXT,
    "bodyFilter" TEXT,
    "resultCount" INTEGER NOT NULL,
    "executionTime" INTEGER NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "search_queries_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "saved_searches" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "filters" TEXT NOT NULL,
    "useCount" INTEGER NOT NULL DEFAULT 0,
    "lastUsedAt" DATETIME,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL,
    CONSTRAINT "saved_searches_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "audit_logs" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT,
    "action" TEXT NOT NULL,
    "resourceType" TEXT,
    "resourceId" TEXT,
    "metadata" TEXT,
    "ipAddress" TEXT NOT NULL,
    "userAgent" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "audit_logs_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "users_gmailAddress_key" ON "users"("gmailAddress");

-- CreateIndex
CREATE INDEX "user_tokens_userId_idx" ON "user_tokens"("userId");

-- CreateIndex
CREATE INDEX "user_tokens_tokenExpiry_idx" ON "user_tokens"("tokenExpiry");

-- CreateIndex
CREATE INDEX "downloaded_files_userId_downloadedAt_idx" ON "downloaded_files"("userId", "downloadedAt");

-- CreateIndex
CREATE INDEX "downloaded_files_expiresAt_idx" ON "downloaded_files"("expiresAt");

-- CreateIndex
CREATE INDEX "downloaded_files_userId_expiresAt_idx" ON "downloaded_files"("userId", "expiresAt");

-- CreateIndex
CREATE INDEX "search_queries_userId_createdAt_idx" ON "search_queries"("userId", "createdAt");

-- CreateIndex
CREATE INDEX "saved_searches_userId_createdAt_idx" ON "saved_searches"("userId", "createdAt");

-- CreateIndex
CREATE INDEX "saved_searches_userId_lastUsedAt_idx" ON "saved_searches"("userId", "lastUsedAt");

-- CreateIndex
CREATE INDEX "audit_logs_userId_createdAt_idx" ON "audit_logs"("userId", "createdAt");

-- CreateIndex
CREATE INDEX "audit_logs_action_createdAt_idx" ON "audit_logs"("action", "createdAt");
