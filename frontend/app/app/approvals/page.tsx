"use client"

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ApiClient } from '@/lib/api/client'
import { useAppProvider } from '@/lib/providers'
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  RefreshCw,
  FileText,
  ChevronRight,
  Filter,
  MessageSquare,
  ExternalLink
} from 'lucide-react'

interface ApprovalItem {
  id: string
  content_project_id: string
  content_draft_id: string
  workspace_id: string
  brand_id: string
  requested_by: string
  reviewed_by?: string | null
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'CHANGES_REQUESTED'
  review_comment?: string | null
  created_at: string
  reviewed_at?: string | null
  draft_title?: string | null
  draft_type?: string | null
  draft_body?: string | null
  project_title?: string | null
}

export default function ApprovalsPage() {
  const { auth } = useAppProvider()
  const { activeBrand } = auth
  const [items, setItems] = useState<ApprovalItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('ALL')
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null)
  const [rejectingId, setRejectingId] = useState<string | null>(null)
  const [rejectComment, setRejectComment] = useState('')
  const [feedbackMessage, setFeedbackMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const fetchApprovals = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const endpoint = statusFilter === 'ALL' ? '/api/approvals' : `/api/approvals?status=${statusFilter}`
      const data = await ApiClient.get<ApprovalItem[]>(endpoint)
      setItems(data || [])
    } catch (err: any) {
      console.error('Failed to fetch approvals:', err)
      setError(err.message || 'Failed to load approvals from the backend.')
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  useEffect(() => {
    fetchApprovals()
  }, [fetchApprovals, activeBrand])

  const handleApprove = async (id: string) => {
    setActionLoadingId(id)
    setFeedbackMessage(null)
    try {
      await ApiClient.post(`/api/approvals/${id}/approve`, {})
      setFeedbackMessage({ type: 'success', text: 'Approval recorded: Content is now APPROVED.' })
      await fetchApprovals()
    } catch (err: any) {
      setFeedbackMessage({ type: 'error', text: err.message || 'Failed to approve content.' })
    } finally {
      setActionLoadingId(null)
    }
  }

  const handleReject = async (id: string) => {
    setActionLoadingId(id)
    setFeedbackMessage(null)
    try {
      await ApiClient.post(`/api/approvals/${id}/reject`, {
        review_comment: rejectComment.trim() || 'Rejected during review.'
      })
      setFeedbackMessage({ type: 'success', text: 'Content marked as REJECTED.' })
      setRejectingId(null)
      setRejectComment('')
      await fetchApprovals()
    } catch (err: any) {
      setFeedbackMessage({ type: 'error', text: err.message || 'Failed to reject content.' })
    } finally {
      setActionLoadingId(null)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return (
          <Badge variant="success" className="flex items-center gap-1.5 py-1 px-2.5">
            <CheckCircle2 className="w-3.5 h-3.5" /> Approved
          </Badge>
        )
      case 'REJECTED':
        return (
          <Badge variant="danger" className="flex items-center gap-1.5 py-1 px-2.5">
            <XCircle className="w-3.5 h-3.5" /> Rejected
          </Badge>
        )
      case 'CHANGES_REQUESTED':
        return (
          <Badge variant="secondary" className="flex items-center gap-1.5 py-1 px-2.5">
            <AlertCircle className="w-3.5 h-3.5" /> Changes Requested
          </Badge>
        )
      case 'PENDING':
      default:
        return (
          <Badge variant="warning" className="flex items-center gap-1.5 py-1 px-2.5">
            <Clock className="w-3.5 h-3.5" /> Pending Review
          </Badge>
        )
    }
  }

  const filterTabs = [
    { label: 'All Reviews', value: 'ALL' },
    { label: 'Pending', value: 'PENDING' },
    { label: 'Approved', value: 'APPROVED' },
    { label: 'Rejected', value: 'REJECTED' },
  ]

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--color-border-primary)] pb-6">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-text-primary)]">
            Approval Queue
          </h1>
          <p className="text-[var(--color-text-tertiary)] text-base mt-1">
            Enforce compliance, review draft content, and authorize publication pipelines.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={fetchApprovals}
            disabled={loading}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Link href="/app/content">
            <Button variant="outline" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Content Studio
            </Button>
          </Link>
        </div>
      </div>

      {/* Global Feedback Banner */}
      {feedbackMessage && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between text-sm ${
            feedbackMessage.type === 'success'
              ? 'bg-emerald-50/80 border-emerald-200 text-emerald-800 dark:bg-emerald-950/40 dark:border-emerald-800 dark:text-emerald-300'
              : 'bg-red-50/80 border-red-200 text-red-800 dark:bg-red-950/40 dark:border-red-800 dark:text-red-300'
          }`}
        >
          <div className="flex items-center gap-2">
            {feedbackMessage.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 shrink-0" />
            )}
            <span>{feedbackMessage.text}</span>
          </div>
          <button
            onClick={() => setFeedbackMessage(null)}
            className="text-xs font-semibold hover:underline ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-[var(--color-border-primary)] pb-2">
        <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mr-2 flex items-center gap-1.5">
          <Filter className="w-3.5 h-3.5" /> Filter:
        </span>
        {filterTabs.map(tab => (
          <button
            key={tab.value}
            onClick={() => setStatusFilter(tab.value)}
            className={`px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all ${
              statusFilter === tab.value
                ? 'bg-[var(--color-accent)] text-white shadow-sm'
                : 'bg-[var(--color-bg-subtle)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-border-primary)]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Error State */}
      {error && (
        <div className="p-8 text-center border border-red-200 bg-red-50/50 dark:bg-red-950/20 dark:border-red-900 rounded-xl space-y-4">
          <AlertCircle className="w-10 h-10 text-red-500 mx-auto" />
          <div>
            <h3 className="font-semibold text-red-900 dark:text-red-200 text-lg">Unable to load approvals</h3>
            <p className="text-sm text-red-600 dark:text-red-400 mt-1 max-w-md mx-auto">{error}</p>
          </div>
          <Button variant="outline" onClick={fetchApprovals} className="border-red-300 hover:bg-red-100 dark:border-red-800">
            <RefreshCw className="w-4 h-4 mr-2" /> Try Again
          </Button>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && !error && (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <Card key={i} className="animate-pulse bg-[var(--color-bg-surface)] border-[var(--color-border-primary)]">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-2.5 flex-1">
                    <div className="h-5 bg-[var(--color-bg-subtle)] rounded w-1/3"></div>
                    <div className="h-3.5 bg-[var(--color-bg-subtle)] rounded w-2/3"></div>
                    <div className="flex gap-4 pt-1">
                      <div className="h-4 bg-[var(--color-bg-subtle)] rounded w-20"></div>
                      <div className="h-4 bg-[var(--color-bg-subtle)] rounded w-24"></div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <div className="h-9 w-20 bg-[var(--color-bg-subtle)] rounded-lg"></div>
                    <div className="h-9 w-24 bg-[var(--color-bg-subtle)] rounded-lg"></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && items.length === 0 && (
        <div className="p-16 text-center border border-dashed border-[var(--color-border-primary)] bg-[var(--color-bg-surface)] rounded-2xl space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto shadow-sm">
            <CheckCircle2 className="w-7 h-7" />
          </div>
          <div className="max-w-md mx-auto">
            <h3 className="font-semibold text-lg text-[var(--color-text-primary)]">
              {statusFilter === 'ALL' ? 'No Approvals Found' : `No ${statusFilter.toLowerCase()} approvals`}
            </h3>
            <p className="text-sm text-[var(--color-text-tertiary)] mt-1.5">
              {statusFilter === 'PENDING'
                ? 'All pending content has been reviewed. Great work maintaining the publication standard!'
                : 'There are no approval requests matching your current filter.'}
            </p>
          </div>
          <Link href="/app/content">
            <Button variant="outline" className="mt-2">
              View All Content
            </Button>
          </Link>
        </div>
      )}

      {/* Approval Items List */}
      {!loading && !error && items.length > 0 && (
        <div className="space-y-4">
          {items.map(app => {
            const isActing = actionLoadingId === app.id
            const isRejecting = rejectingId === app.id

            return (
              <Card
                key={app.id}
                className="transition-all duration-200 hover:shadow-md border-[var(--color-border-primary)] bg-[var(--color-bg-surface)] overflow-hidden"
              >
                <CardContent className="p-6">
                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
                    {/* Item Information */}
                    <div className="space-y-3 flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-3">
                        <Link
                          href={`/app/content/${app.content_draft_id}`}
                          className="group inline-flex items-center gap-1.5 text-lg font-semibold text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors"
                        >
                          <span className="truncate">{app.draft_title || 'Untitled Draft'}</span>
                          <ExternalLink className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity shrink-0" />
                        </Link>
                        {getStatusBadge(app.status)}
                        {app.draft_type && (
                          <Badge variant="secondary" className="text-xs uppercase tracking-wider font-mono">
                            {app.draft_type}
                          </Badge>
                        )}
                      </div>

                      {app.project_title && (
                        <p className="text-xs text-[var(--color-text-secondary)]">
                          Project: <span className="font-medium text-[var(--color-text-primary)]">{app.project_title}</span>
                        </p>
                      )}

                      {app.draft_body && (
                        <p className="text-sm text-[var(--color-text-tertiary)] line-clamp-2 bg-[var(--color-bg-subtle)] p-3 rounded-lg border border-[var(--color-border-primary)] font-serif leading-relaxed">
                          {app.draft_body}
                        </p>
                      )}

                      {/* Review Comment display if present */}
                      {app.review_comment && (
                        <div className="flex items-start gap-2 text-xs bg-amber-50/70 dark:bg-amber-950/30 text-amber-900 dark:text-amber-300 p-2.5 rounded-lg border border-amber-200 dark:border-amber-800">
                          <MessageSquare className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                          <div>
                            <span className="font-semibold">Reviewer Notes: </span>
                            <span>{app.review_comment}</span>
                          </div>
                        </div>
                      )}

                      {/* Metadata row */}
                      <div className="flex flex-wrap items-center gap-4 text-xs text-[var(--color-text-muted)] pt-1">
                        <span>Submitted: {new Date(app.created_at).toLocaleString()}</span>
                        {app.reviewed_at && (
                          <span>Reviewed: {new Date(app.reviewed_at).toLocaleString()}</span>
                        )}
                        <Link
                          href={`/app/content/${app.content_draft_id}`}
                          className="text-[var(--color-accent)] hover:underline inline-flex items-center gap-1"
                        >
                          View Full Content <ChevronRight className="w-3 h-3" />
                        </Link>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row items-center gap-2.5 shrink-0">
                      {app.status === 'PENDING' ? (
                        <>
                          <Button
                            variant="outline"
                            disabled={isActing}
                            onClick={() => {
                              if (isRejecting) {
                                setRejectingId(null)
                                setRejectComment('')
                              } else {
                                setRejectingId(app.id)
                              }
                            }}
                            className="w-full sm:w-auto text-red-600 border-red-200 hover:bg-red-50 dark:hover:bg-red-950/30 dark:border-red-800"
                          >
                            {isRejecting ? 'Cancel Reject' : 'Reject'}
                          </Button>
                          <Button
                            disabled={isActing}
                            onClick={() => handleApprove(app.id)}
                            className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-1.5 shadow-sm"
                          >
                            <CheckCircle2 className="w-4 h-4" />
                            {isActing ? 'Approving...' : 'Approve'}
                          </Button>
                        </>
                      ) : (
                        <Link href={`/app/content/${app.content_draft_id}`}>
                          <Button variant="outline" size="sm" className="w-full sm:w-auto">
                            Manage Content
                          </Button>
                        </Link>
                      )}
                    </div>
                  </div>

                  {/* Inline Rejection Reason Panel */}
                  {isRejecting && (
                    <div className="mt-4 pt-4 border-t border-[var(--color-border-primary)] space-y-3">
                      <label className="block text-xs font-medium text-[var(--color-text-secondary)]">
                        Reason for Rejection (Optional but recommended):
                      </label>
                      <textarea
                        rows={2}
                        value={rejectComment}
                        onChange={e => setRejectComment(e.target.value)}
                        placeholder="Provide clear actionable feedback for the marketing team..."
                        className="w-full text-sm p-2.5 rounded-lg border border-[var(--color-border-primary)] bg-[var(--color-bg-base)] text-[var(--color-text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent)]"
                      />
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setRejectingId(null)
                            setRejectComment('')
                          }}
                        >
                          Cancel
                        </Button>
                        <Button
                          size="sm"
                          disabled={isActing}
                          onClick={() => handleReject(app.id)}
                          className="bg-red-600 hover:bg-red-700 text-white"
                        >
                          {isActing ? 'Rejecting...' : 'Confirm Rejection'}
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
