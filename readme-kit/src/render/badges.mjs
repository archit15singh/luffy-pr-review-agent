/**
 * shields.io badge helpers.
 *
 * Private GitHub repos cannot use github/* status endpoints (shields returns
 * "repo or workflow not found"). Static badges must use the query form
 * (`/static/v1?...`) so messages may contain `/`, `-`, `@`, spaces safely.
 */

function q(params) {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v == null || v === "") continue;
    sp.set(k, String(v));
  }
  return sp.toString();
}

/** Static badge via query API (handles special chars in label/message). */
export function staticBadgeUrl({
  label,
  message,
  color,
  style = "for-the-badge",
  logo,
  logoColor,
  labelColor,
}) {
  const params = {
    label: label || "",
    message: message || "",
    color: color || "lightgrey",
    style,
  };
  if (logo) params.logo = logo;
  if (logoColor) params.logoColor = logoColor;
  if (labelColor) params.labelColor = labelColor;
  return `https://img.shields.io/static/v1?${q(params)}`;
}

/**
 * @param {object} badge
 * @param {object} theme
 * @param {object} repo  { owner, name, default_branch, private? }
 */
export function renderBadge(badge, theme, repo) {
  const style = theme.badgeStyle || "for-the-badge";
  const owner = repo?.owner || "owner";
  const name = repo?.name || "repo";
  const branch = repo?.default_branch || "main";
  const ink = (theme.colors && theme.colors.ink) || "0B0F19";
  const flame = (theme.colors && theme.colors.flame) || "FF6B2C";
  const gold = (theme.colors && theme.colors.gold) || "FFD166";
  // Private by default for this product; set repo.private: false for live GH badges
  const isPrivate = repo?.private !== false && repo?.private !== "false";

  if (badge.type === "workflow") {
    const wf = badge.workflow;
    const label = badge.label || "CI";
    const href = `https://github.com/${owner}/${name}/actions/workflows/${wf}`;
    if (isPrivate || badge.static) {
      // Live Actions status is invisible on private repos via shields.io
      const message = badge.message || "Actions";
      const color = badge.color || "2ea44f"; // github green success-ish
      const url = staticBadgeUrl({
        label,
        message,
        color,
        style,
        logo: badge.logo || "githubactions",
        logoColor: "white",
      });
      return `[![${label}](${url})](${href})`;
    }
    const url =
      `https://img.shields.io/github/actions/workflow/status/${owner}/${name}/${wf}` +
      `?branch=${encodeURIComponent(branch)}&style=${style}` +
      `&label=${encodeURIComponent(label)}&logo=githubactions&logoColor=white`;
    return `[![${label}](${url})](${href})`;
  }

  if (badge.type === "last-commit") {
    const href = `https://github.com/${owner}/${name}/commits/${branch}`;
    if (isPrivate || badge.static) {
      const url = staticBadgeUrl({
        label: badge.label || "branch",
        message: badge.message || branch,
        color: badge.color || ink,
        style,
        logo: badge.logo || "git",
        logoColor: "white",
      });
      return `[![Last commit](${url})](${href})`;
    }
    const url =
      `https://img.shields.io/github/last-commit/${owner}/${name}/${branch}` +
      `?style=${style}&logo=git&logoColor=white&color=${ink}`;
    return `[![Last commit](${url})](${href})`;
  }

  if (badge.type === "license") {
    const lic = badge.message || "MIT";
    const color = badge.color || gold;
    const url = staticBadgeUrl({
      label: "license",
      message: lic,
      color,
      style,
      labelColor: ink,
      logo: "open-source-initiative",
      logoColor: color,
    });
    return `![License](${url})`;
  }

  // static (or any free-form badge)
  const label = badge.label || "info";
  const message = badge.message || "";
  const color = badge.color || flame;
  const url = staticBadgeUrl({
    label,
    message,
    color,
    style,
    logo: badge.logo,
    logoColor: badge.logoColor || (badge.logo ? "white" : undefined),
    labelColor: badge.labelColor,
  });
  if (badge.href) {
    return `[![${label}](${url})](${badge.href})`;
  }
  return `![${label}](${url})`;
}

export function renderBadgeRow(badges, theme, repo) {
  if (!badges?.length) return "";
  return badges.map((b) => renderBadge(b, theme, repo)).join("\n");
}
