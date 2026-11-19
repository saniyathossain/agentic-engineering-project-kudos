#!/usr/bin/env bash
# Creates (up) or removes (down) a second, verified owner with one space and one testimonial, so the collections can
# test the 403 "another owner's space" case. Dev stack only: it writes to the dev database through artisan tinker.
#
#   docs/api/scripts/foreign-space.sh up     prints foreignSpaceId and foreignTestimonialId
#   docs/api/scripts/foreign-space.sh down   deletes that user, its space and its testimonial
set -euo pipefail
cd "$(dirname "$0")/../../.."
DC=(docker compose -f docker/docker-compose.yml)
EMAIL="api-foreign@kudos.test"

case "${1:-}" in
  up)
    "${DC[@]}" exec -T app php artisan tinker --execute='
      $u = App\Models\User::query()->firstOrCreate(["email" => "'"$EMAIL"'"], ["name" => "API Foreign Owner", "password" => bin2hex(random_bytes(12))]);
      $u->forceFill(["email_verified_at" => now()])->save();
      $s = $u->spaces()->first() ?? $u->spaces()->create(["name" => "Foreign Probe", "slug" => "foreign-probe-" . bin2hex(random_bytes(3)), "header_title" => "Hi", "message" => "m",
          "collect_rating" => false, "theme" => App\Enums\SpaceTheme::Light, "fields" => [], "is_accepting" => true]);
      $t = $s->testimonials()->first() ?? $s->testimonials()->create(["rating" => null, "body" => "Foreign testimonial", "respondent_name" => "Foreign", "respondent_email" => "foreign@example.com",
          "status" => App\Enums\TestimonialStatus::Pending, "is_favorite" => false, "consent" => true, "submitted_at" => now()]);
      echo "foreignSpaceId=" . $s->public_id . "\nforeignTestimonialId=" . $t->public_id . "\n";'
    ;;
  down)
    "${DC[@]}" exec -T app php artisan tinker --execute='
      $u = App\Models\User::query()->where("email", "'"$EMAIL"'")->first();
      if ($u) { $u->spaces()->get()->each(function ($s) { $s->testimonials()->delete(); $s->delete(); }); $u->delete(); }
      echo "removed\n";'
    ;;
  *)
    echo "usage: $0 up|down" >&2
    exit 2
    ;;
esac
