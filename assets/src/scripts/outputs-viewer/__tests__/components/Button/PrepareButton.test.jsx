/* eslint-disable no-console */
import userEvent from "@testing-library/user-event";
import React from "react";
import { afterAll, beforeEach, describe, expect, it, vi } from "vitest";
import PrepareButton from "../../../components/Button/PrepareButton";
import * as useFileList from "../../../hooks/use-file-list";
import * as toast from "../../../utils/toast";
import { server, rest } from "../../__mocks__/server";
import { fileList } from "../../helpers/files";
import props, { prepareUrl } from "../../helpers/props";
import { render, screen, waitFor } from "../../test-utils";

describe("<PrepareButton />", () => {
  const urls = {
    redirect: "http://localhost/prepare-redirect",
  };

  const { authToken, csrfToken, filesUrl } = props;

  const fileIds = ["abc1", "abc2", "abc3", "abc4"];

  beforeEach(() => {
    /**
     * Mock window
     */
    Object.defineProperty(window, "location", {
      value: {},
      writable: true,
    });
  });

  afterAll(() => {
    vi.resetAllMocks();
  });

  it("hides the element if there are no files", () => {
    vi.spyOn(useFileList, "default").mockImplementation(() => ({
      data: [],
    }));

    const { container } = render(
      <PrepareButton
        authToken={authToken}
        csrfToken={csrfToken}
        filesUrl={filesUrl}
        prepareUrl={prepareUrl}
      />
    );

    expect(container).toBeEmptyDOMElement();
  });

  it("shows if there are files", () => {
    vi.spyOn(useFileList, "default").mockImplementation(() => ({
      data: fileList,
    }));

    render(
      <PrepareButton
        authToken={authToken}
        csrfToken={csrfToken}
        filesUrl={filesUrl}
        prepareUrl={prepareUrl}
      />
    );

    expect(screen.getByRole("button")).toHaveTextContent("Publish");
  });

  it("triggers a mutation on click", async () => {
    const user = userEvent.setup();
    vi.spyOn(useFileList, "default").mockImplementation(() => ({
      data: fileList,
    }));

    server.use(
      rest.post(prepareUrl, async (req, res, ctx) => {
        const jsonBody = await req.json();
        await expect(jsonBody.file_ids).toEqual(fileIds);

        return res(
          ctx.json({
            url: urls.redirect,
          })
        );
      })
    );

    render(
      <PrepareButton
        authToken={authToken}
        csrfToken={csrfToken}
        filesUrl={filesUrl}
        prepareUrl={prepareUrl}
      />
    );

    expect(screen.getByRole("button")).toHaveTextContent("Publish");

    await user.click(screen.getByRole("button"));

    await waitFor(() =>
      expect(screen.getByRole("button")).toHaveTextContent("Publishing…")
    );
    await waitFor(() => expect(window.location.href).toEqual(urls.redirect));
  });

  it("show the JSON error message", async () => {
    const user = userEvent.setup();
    const toastError = vi.fn();
    console.error = vi.fn();

    vi.spyOn(useFileList, "default").mockImplementation(() => ({
      data: fileList,
    }));

    vi.spyOn(toast, "toastError").mockImplementation(toastError);

    server.use(
      rest.post(prepareUrl, async (req, res, ctx) => {
        const jsonBody = await req.json();
        await expect(jsonBody.file_ids).toEqual(fileIds);

        return res(ctx.status(403), ctx.json({ detail: "Invalid user token" }));
      })
    );

    render(
      <PrepareButton
        authToken={authToken}
        csrfToken={csrfToken}
        filesUrl={filesUrl}
        prepareUrl={prepareUrl}
      />
    );

    expect(screen.getByRole("button")).toHaveTextContent("Publish");

    await user.click(screen.getByRole("button"));

    await waitFor(() =>
      expect(screen.getByRole("button")).toHaveTextContent("Publishing…")
    );
    await waitFor(() =>
      expect(toastError).toHaveBeenCalledWith({
        message: "Error: Invalid user token",
        prepareUrl,
        toastId: "PrepareButton",
        url: "http://localhost:3000/",
      })
    );
  });

  it("show the server error message", async () => {
    const user = userEvent.setup();
    const toastError = vi.fn();
    console.error = vi.fn();

    vi.spyOn(useFileList, "default").mockImplementation(() => ({
      data: fileList,
    }));

    vi.spyOn(toast, "toastError").mockImplementation(toastError);

    server.use(
      rest.post(prepareUrl, async (req, res, ctx) => {
        const jsonBody = await req.json();
        await expect(jsonBody.file_ids).toEqual(fileIds);

        return res(ctx.status(500), ctx.json({}));
      })
    );

    render(
      <PrepareButton
        authToken={authToken}
        csrfToken={csrfToken}
        filesUrl={filesUrl}
        prepareUrl={prepareUrl}
      />
    );

    expect(screen.getByRole("button")).toHaveTextContent("Publish");

    await user.click(screen.getByRole("button"));

    await waitFor(() =>
      expect(screen.getByRole("button")).toHaveTextContent("Publishing…")
    );
    await waitFor(() =>
      expect(toastError).toHaveBeenCalledWith({
        message: "Error",
        prepareUrl,
        toastId: "PrepareButton",
        url: "http://localhost:3000/",
      })
    );
  });
});
