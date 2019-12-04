do $$
declare
    data_set d_data_set.name%TYPE := 'Corine Land Cover';
begin
    delete from document_keyword where document_id in (
        select id from document where data_set_id = (select id from d_data_set where name = data_set)
    );
    delete from document_file_language where documentfile_id in (
        select id from document_file where document_id in (
            select id from document where data_set_id = (select id from d_data_set where name = data_set)
        )
    );
    delete from document_file where document_id in (
        select id from document where data_set_id = (select id from d_data_set where name = data_set)
    );
    delete from document_country where document_id in (
        select id from document where data_set_id = (select id from d_data_set where name = data_set)
    );
    delete from document_nuts_level where document_id in (
        select id from document where data_set_id = (select id from d_data_set where name = data_set)
    );
    delete from geographic_bounds where document_id in (
        select id from document where data_set_id = (select id from d_data_set where name = data_set)
    );
    delete from document_higher_level_docs where
        from_document_id in (
        select id from document where data_set_id = (select id from d_data_set where name = data_set)
        )
        or
        to_document_id in (
        select id from document where data_set_id = (select id from d_data_set where name = data_set)
        );
    delete from document_same_level_docs where
        from_document_id in (
        select id from document where data_set_id = (select id from d_data_set where name = data_set)
        )
        or
        to_document_id in (
        select id from document where data_set_id = (select id from d_data_set where name = data_set)
        );
    delete from document_lower_level_docs where
        from_document_id in (
        select id from document where data_set_id = (select id from d_data_set where name = data_set)
        )
        or
        to_document_id in (
        select id from document where data_set_id = (select id from d_data_set where name = data_set)
        );
    delete from document where data_set_id = (select id from d_data_set where name = data_set);
end $$;